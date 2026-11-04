import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
CHAVE = os.getenv("TMDB_API_KEY")
BASE = "https://api.themoviedb.org/3"

# sessao reaproveita a conexao e tenta de novo se ela cair
sessao = requests.Session()
tentativas = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
sessao.mount("https://", HTTPAdapter(max_retries=tentativas))

# o TMDB usa nomes diferentes pra filme e pra serie
CAMPOS = {
    "filme": {"rota": "movie", "titulo": "title", "data": "release_date", "kw": "keywords"},
    "serie": {"rota": "tv", "titulo": "name", "data": "first_air_date", "kw": "results"},
}


def pedir(caminho, **params):
    # faz o pedido pro TMDB e devolve o json
    params["api_key"] = CHAVE
    params["language"] = "pt-BR"
    r = sessao.get(BASE + caminho, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def no_banco(conn, tipo, id):
    # confere se o titulo ja esta salvo
    linha = conn.execute("SELECT 1 FROM titulos WHERE id = ? AND tipo = ?", (id, tipo)).fetchone()
    return linha is not None


def salvar_titulo(conn, tipo, f):
    # junta generos e palavras-chave em texto e grava a linha
    c = CAMPOS[tipo]
    generos = ", ".join(g["name"] for g in f["genres"])
    palavras = ", ".join(k["name"] for k in f["keywords"][c["kw"]])
    ano = (f.get(c["data"]) or "")[:4]
    conn.execute(
        "INSERT OR REPLACE INTO titulos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (f["id"], tipo, f[c["titulo"]], ano, f["overview"],
         generos, palavras, f["vote_average"], f["poster_path"]),
    )


def baixar_e_salvar(conn, tipo, id):
    # busca os detalhes (com palavras-chave) e salva no banco
    rota = CAMPOS[tipo]["rota"]
    detalhes = pedir(f"/{rota}/{id}", append_to_response="keywords")
    salvar_titulo(conn, tipo, detalhes)
