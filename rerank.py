import hashlib
import json
import os
import sqlite3
from pydantic import BaseModel
from google.genai import types
from llm import gerar

ARQUIVO_CACHE = "rerank_cache.json"
MAX_ESCOLHAS = 30


# formato que o LLM precisa devolver
class Escolha(BaseModel):
    numero: int  # numero do candidato na lista que recebeu
    motivo: str  # uma frase curta explicando


class Ranking(BaseModel):
    escolhas: list[Escolha]


INSTRUCAO = f"""Voce ajuda a escolher filmes e series pela vibe (clima e sentimento).
Vai receber o pedido da pessoa e uma lista numerada de candidatos, cada um com titulo, ano, generos e sinopse.
Escolha ate {MAX_ESCOLHAS} candidatos que realmente combinam com a vibe, do que mais combina para o que menos combina.
Pense no clima e no sentimento que o titulo passa, nao so no assunto. Por exemplo, um filme sobre bruxas pode ser sombrio e violento, e nao aconchegante.
Se um candidato nao combina com a vibe, nao inclua.
Se o pedido vier com varias leituras possiveis, aceite candidatos de qualquer uma delas.
O pedido pode estar em qualquer idioma.
Para cada escolha, escreva em uma frase curta, em ingles, por que combina.
Use apenas os numeros da lista."""

_sinopses = None


def sinopse_de(id, tipo):
    # le as sinopses do banco so na primeira vez
    global _sinopses
    if _sinopses is None:
        conn = sqlite3.connect("filmes.db")
        _sinopses = {(i, t): s or "" for i, t, s in conn.execute("SELECT id, tipo, sinopse FROM titulos")}
        conn.close()
    return _sinopses.get((id, tipo), "")


def ler_cache():
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, encoding="utf-8") as arq:
            return json.load(arq)
    return {}


def montar_lista(candidatos):
    # uma linha por candidato: "1. Titulo (ano) [tipo] - generos - sinopse"
    linhas = []
    for n, (id, tipo, titulo, ano, generos) in enumerate(candidatos, start=1):
        sinopse = sinopse_de(id, tipo)[:220]
        linhas.append(f"{n}. {titulo} ({ano}) [{tipo}] - {generos} - {sinopse}")
    return "\n".join(linhas)


def reranquear(vibe, candidatos, leituras=()):
    # candidatos: lista de infos (id, tipo, titulo, ano, generos)
    # leituras: outras interpretacoes possiveis do pedido (quando ele e ambiguo)
    # devolve (infos na nova ordem, {(id, tipo): motivo})
    # a chave do cache muda se o pedido, as leituras ou a lista de candidatos mudar
    # ("v2" separa dos rankings antigos, que tinham motivos em portugues)
    ids = json.dumps([[c[0], c[1]] for c in candidatos])
    base = "v2|" + vibe.strip().lower() + "|" + "|".join(leituras) + ids
    chave = hashlib.sha1(base.encode()).hexdigest()

    cache = ler_cache()
    if chave in cache:
        escolhas = cache[chave]
    else:
        pedido = f'Pedido da pessoa: "{vibe}"\n'
        if leituras:
            pedido += "Leituras possiveis (aceite qualquer uma): " + " / ".join(leituras) + "\n"
        pedido += f"\nCandidatos:\n{montar_lista(candidatos)}"
        res = gerar(
            pedido,
            types.GenerateContentConfig(
                system_instruction=INSTRUCAO,
                response_mime_type="application/json",
                response_schema=Ranking,
                temperature=0,
            ),
        )
        escolhas = [[e.numero, e.motivo] for e in res.parsed.escolhas]
        cache[chave] = escolhas
        with open(ARQUIVO_CACHE, "w", encoding="utf-8") as arq:
            json.dump(cache, arq, ensure_ascii=False)

    # monta a nova ordem: primeiro o que o LLM escolheu, depois o resto na ordem de antes
    ordem = []
    motivos = {}
    for numero, motivo in escolhas:
        if 1 <= numero <= len(candidatos) and candidatos[numero - 1] not in ordem:
            info = candidatos[numero - 1]
            ordem.append(info)
            motivos[(info[0], info[1])] = motivo
    ordem += [c for c in candidatos if c not in ordem]
    return ordem, motivos
