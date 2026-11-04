import argparse
import sqlite3
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODELO = "gemini-embedding-001"


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


def embedding_da_busca(texto):
    # transforma o que foi digitado em numeros (modo pergunta)
    res = client.models.embed_content(
        model=MODELO,
        contents=texto,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return np.array(res.embeddings[0].values, dtype=np.float32)


def buscar(texto, infos, vetores, quantos=10, tipo=None):
    q = embedding_da_busca(texto)
    # similaridade do cosseno: produto escalar dividido pelos tamanhos
    sim = vetores @ q / (np.linalg.norm(vetores, axis=1) * np.linalg.norm(q))
    if tipo:
        # derruba a nota de quem nao e do tipo pedido
        for i, info in enumerate(infos):
            if info[1] != tipo:
                sim[i] = -1
    melhores = np.argsort(sim)[::-1][:quantos]
    return [(infos[i], float(sim[i])) for i in melhores]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("busca", nargs="+")  # a busca vem do terminal
    parser.add_argument("--tipo", choices=["filme", "serie"])  # filtro opcional
    args = parser.parse_args()

    infos, vetores = carregar_titulos()
    for (_, tipo, titulo, ano, generos), nota in buscar(" ".join(args.busca), infos, vetores, tipo=args.tipo):
        print(f"{nota:.3f}  {titulo} ({ano}) [{tipo}]  [{generos}]")


if __name__ == "__main__":
    main()
