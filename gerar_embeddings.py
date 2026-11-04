import sqlite3
import time
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODELO = "gemini-embedding-001"
LOTE = 20  # titulos por pedido


def texto_do_titulo(f):
    # junta tudo que descreve o titulo num texto so
    titulo, ano, sinopse, generos, palavras = f
    return f"{titulo} ({ano}). Generos: {generos}. Palavras-chave: {palavras}. Sinopse: {sinopse}"


def gerar(textos):
    # pede os embeddings; se der erro, espera e tenta de novo
    for tentativa in range(5):
        try:
            res = client.models.embed_content(
                model=MODELO,
                contents=textos,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return [e.values for e in res.embeddings]
        except Exception as erro:
            print("erro, esperando:", str(erro)[:100])
            time.sleep(10 * (tentativa + 1))
    raise RuntimeError("nao consegui gerar os embeddings")


def main():
    conn = sqlite3.connect("filmes.db")

    # so os titulos que ainda nao tem embedding
    pendentes = conn.execute("""
        SELECT t.id, t.tipo, t.titulo, t.ano, t.sinopse, t.generos, t.palavras_chave
        FROM titulos t
        LEFT JOIN embeddings e ON e.id = t.id AND e.tipo = t.tipo
        WHERE e.id IS NULL
    """).fetchall()
    print("faltam:", len(pendentes))

    for i in range(0, len(pendentes), LOTE):
        lote = pendentes[i:i + LOTE]
        textos = [texto_do_titulo(p[2:]) for p in lote]
        vetores = gerar(textos)
        for p, v in zip(lote, vetores):
            # guarda a lista de numeros como bytes
            conn.execute("INSERT OR REPLACE INTO embeddings (id, tipo, vetor) VALUES (?, ?, ?)",
                         (p[0], p[1], np.array(v, dtype=np.float32).tobytes()))
        conn.commit()
        print(i + len(lote), "de", len(pendentes))
        time.sleep(1)

    conn.close()


main()
