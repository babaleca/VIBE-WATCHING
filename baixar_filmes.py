import os
import time
import sqlite3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
CHAVE = os.getenv("TMDB_API_KEY")
BASE = "https://api.themoviedb.org/3"
PAGINAS = 50  # cada pagina tem 20 filmes

# sessao reaproveita a conexao e tenta de novo se ela cair
sessao = requests.Session()
tentativas = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
sessao.mount("https://", HTTPAdapter(max_retries=tentativas))


def pedir(caminho, **params):
    # faz o pedido pro TMDB e devolve o json
    params["api_key"] = CHAVE
    params["language"] = "pt-BR"
    r = sessao.get(BASE + caminho, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def criar_tabela(conn):
    # cria a tabela se ainda nao existir
    conn.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY,
            titulo TEXT,
            ano TEXT,
            sinopse TEXT,
            generos TEXT,
            palavras_chave TEXT,
            nota REAL,
            poster TEXT
        )
    """)


def salvar_filme(conn, f):
    # junta generos e palavras-chave em texto e grava a linha
    generos = ", ".join(g["name"] for g in f["genres"])
    palavras = ", ".join(k["name"] for k in f["keywords"]["keywords"])
    conn.execute(
        "INSERT OR REPLACE INTO filmes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (f["id"], f["title"], f["release_date"][:4], f["overview"],
         generos, palavras, f["vote_average"], f["poster_path"]),
    )


def main():
    conn = sqlite3.connect("filmes.db")
    criar_tabela(conn)
    # ids que ja estao no banco, pra nao baixar de novo
    ja_salvos = {linha[0] for linha in conn.execute("SELECT id FROM filmes")}

    for pagina in range(1, PAGINAS + 1):
        # lista dos filmes mais votados
        lista = pedir("/discover/movie", sort_by="vote_count.desc", page=pagina)
        for item in lista["results"]:
            if item["id"] in ja_salvos:
                continue
            # detalhes de cada filme, ja com as palavras-chave
            filme = pedir(f"/movie/{item['id']}", append_to_response="keywords")
            salvar_filme(conn, filme)
            time.sleep(0.05)  # pausa pra nao sobrecarregar a API
        conn.commit()
        print("pagina", pagina, "ok")

    total = conn.execute("SELECT COUNT(*) FROM filmes").fetchone()[0]
    print("filmes salvos:", total)
    for linha in conn.execute("SELECT titulo, ano, palavras_chave FROM filmes LIMIT 3"):
        print(linha)
    conn.close()


main()
