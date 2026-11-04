import argparse
import json
import os
import sqlite3
import unicodedata
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types
from reescrever import reescrever
from rerank import reranquear

load_dotenv()
client = genai.Client()
MODELO = "gemini-embedding-001"
ARQUIVO_CACHE = "cache_embeddings.json"

# genero que o LLM sugere tirar nao e certeza, entao so desconta um pouco da nota
PENALIDADE_IA = 0.05

# quantos candidatos a busca entrega pro LLM reordenar
# (medi: com 50 so 33 de 65 titulos esperados estavam ao alcance, com 80 sao 40)
CANDIDATOS = 80

# na mistura de varias buscas (RRF), quanto maior, menos o topo pesa
K_RRF = 60

# as series do TMDB usam nomes de genero diferentes dos filmes
EQUIVALENTES = {
    "acao": ["action & adventure"],
    "aventura": ["action & adventure"],
    "ficcao cientifica": ["sci-fi & fantasy"],
    "fantasia": ["sci-fi & fantasy"],
    "guerra": ["war & politics"],
}


def normalizar(texto):
    # tira acento e deixa minusculo: "Ação" e "acao" viram a mesma coisa
    sem_acento = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower().strip()


def generos_proibidos(excluir):
    # lista de generos que a pessoa nao quer, ja com os nomes usados nas series
    proibidos = set()
    for g in excluir:
        nome = normalizar(g)
        proibidos.add(nome)
        proibidos.update(EQUIVALENTES.get(nome, []))
    return proibidos


def tem_proibido(generos, proibidos):
    # generos vem do banco assim: "Fantasia, Romance"
    return any(normalizar(g) in proibidos for g in (generos or "").split(","))


def carregar_titulos():
    # le os titulos e os vetores do banco
    conn = sqlite3.connect("filmes.db")
    linhas = conn.execute("""
        SELECT t.id, t.tipo, t.titulo, t.ano, t.generos, e.vetor
        FROM titulos t JOIN embeddings e ON e.id = t.id AND e.tipo = t.tipo
    """).fetchall()
    conn.close()
    infos = [(l[0], l[1], l[2], l[3], l[4]) for l in linhas]
    # transforma os bytes de volta em lista de numeros
    vetores = np.array([np.frombuffer(l[5], dtype=np.float32) for l in linhas])
    return infos, vetores


def ler_cache():
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, encoding="utf-8") as arq:
            return json.load(arq)
    return {}


def embedding_da_busca(texto):
    # se esse texto ja foi transformado em numeros antes, usa o que esta salvo
    cache = ler_cache()
    if texto in cache:
        return np.array(cache[texto], dtype=np.float32)

    # transforma o que foi digitado em numeros (modo pergunta)
    res = client.models.embed_content(
        model=MODELO,
        contents=texto,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    vetor = np.array(res.embeddings[0].values, dtype=np.float32)

    cache[texto] = vetor.tolist()
    with open(ARQUIVO_CACHE, "w", encoding="utf-8") as arq:
        json.dump(cache, arq)
    return vetor


def calcular_sim(texto, infos, vetores, tipo=None, excluir=(), excluir_suave=()):
    q = embedding_da_busca(texto)
    # similaridade do cosseno: produto escalar dividido pelos tamanhos
    sim = vetores @ q / (np.linalg.norm(vetores, axis=1) * np.linalg.norm(q))

    duros = generos_proibidos(excluir)  # o que a pessoa marcou: sai da lista
    suaves = generos_proibidos(excluir_suave)  # o que o LLM sugeriu: so perde nota
    for i, info in enumerate(infos):
        if tipo and info[1] != tipo:
            sim[i] = -1
        elif tem_proibido(info[4], duros):
            sim[i] = -1
        elif tem_proibido(info[4], suaves):
            sim[i] -= PENALIDADE_IA
    return sim


def buscar(texto, infos, vetores, quantos=10, tipo=None, excluir=(), excluir_suave=()):
    sim = calcular_sim(texto, infos, vetores, tipo, excluir, excluir_suave)
    melhores = np.argsort(sim)[::-1][:quantos]
    return [(infos[i], float(sim[i])) for i in melhores if sim[i] > -1]


def buscar_varios(textos, infos, vetores, quantos=10, tipo=None, excluir=(), excluir_suave=()):
    # busca com cada texto e mistura as listas (RRF): quem aparece bem em varias sobe
    # usado quando o pedido e ambiguo e o LLM deu varias leituras
    if len(textos) == 1:
        return buscar(textos[0], infos, vetores, quantos, tipo, excluir, excluir_suave)

    todas = [calcular_sim(t, infos, vetores, tipo, excluir, excluir_suave) for t in textos]
    pontos = np.zeros(len(infos))
    for sim in todas:
        validos = [i for i in np.argsort(sim)[::-1] if sim[i] > -1]
        for posicao, i in enumerate(validos):
            pontos[i] += 1 / (K_RRF + posicao + 1)

    maior_sim = np.max(todas, axis=0)  # a nota mostrada e a melhor entre as buscas
    melhores = [i for i in np.argsort(pontos)[::-1] if maior_sim[i] > -1][:quantos]
    return [(infos[i], float(maior_sim[i])) for i in melhores]


def buscar_vibe(vibe, infos, vetores, quantos=10, tipo=None, excluir=(), metodo="rerank"):
    # metodo "puro": usa so o que a pessoa digitou
    # metodo "reescrito": usa so a descricao que o LLM escreveu
    # metodo "combinado": usa os dois juntos
    # metodo "rerank": busca "combinado" e o LLM reordena os melhores (CANDIDATOS)
    # em "combinado" e "rerank", se o pedido for ambiguo, cada leitura vira uma busca extra
    # devolve: (resultado, reescrita, motivos)
    textos = [vibe]
    excluir_ia = []
    leituras = []
    reescrita = None
    if metodo != "puro":
        try:
            reescrita = reescrever(vibe)
            if metodo == "reescrito":
                textos = [reescrita.descricao]
            else:
                textos = [f"{vibe}. {reescrita.descricao}"]
                # pedido ambiguo: cada leitura vira mais uma busca (sem a palavra ambigua)
                leituras = list(reescrita.leituras)
                textos += leituras
            excluir_ia = reescrita.excluir_generos
        except Exception as erro:
            print(f"a reescrita falhou ({erro}), usando a busca pura")

    if metodo != "rerank":
        resultado = buscar_varios(textos, infos, vetores, quantos, tipo, excluir, excluir_ia)
        return resultado, reescrita, {}

    # pega os candidatos, deixa o LLM reordenar, e devolve na nova ordem
    candidatos = buscar_varios(textos, infos, vetores, max(CANDIDATOS, quantos), tipo, excluir, excluir_ia)
    notas = {(info[0], info[1]): nota for info, nota in candidatos}
    try:
        ordem, motivos = reranquear(vibe, [info for info, nota in candidatos], leituras)
    except Exception as erro:
        print(f"o reranking falhou ({erro}), usando a ordem da busca")
        return candidatos[:quantos], reescrita, {}
    resultado = [(info, notas[(info[0], info[1])]) for info in ordem[:quantos]]
    return resultado, reescrita, motivos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("busca", nargs="+")  # a busca vem do terminal
    parser.add_argument("--tipo", choices=["filme", "serie"])  # filtro opcional
    parser.add_argument("--metodo", choices=["puro", "reescrito", "combinado", "rerank"], default="rerank")
    parser.add_argument("--sem", nargs="*", default=[])  # generos pra excluir
    args = parser.parse_args()

    infos, vetores = carregar_titulos()
    resultado, reescrita, motivos = buscar_vibe(
        " ".join(args.busca), infos, vetores, tipo=args.tipo, excluir=args.sem, metodo=args.metodo
    )
    if reescrita:
        print("entendi:", reescrita.resumo or reescrita.descricao)
        for leitura in reescrita.leituras:
            print("  leitura:", leitura)
    for (id, tipo, titulo, ano, generos), nota in resultado:
        print(f"{nota:.3f}  {titulo} ({ano}) [{tipo}]  [{generos}]")
        if (id, tipo) in motivos:
            print(f"       {motivos[(id, tipo)]}")


if __name__ == "__main__":
    main()
