import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from . import llm
from .search import carregar_titulos, buscar_vibe

llm.RODADAS = 1  # na API, se o LLM estiver ocupado, falha rapido e a busca segue sem ele
llm.PAUSA_SEGUNDOS = 60  # e depois de falhar, nem tenta de novo por 1 minuto
llm.TEMPO_MAXIMO = 40  # e cada etapa com LLM tem no maximo 40s no total

app = FastAPI(title="Vibe Watching")

# deixa a interface (que roda em outra porta) conversar com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# carrega tudo UMA vez, quando a API liga (e rapido: sao so 1500 vetores)
infos, vetores = carregar_titulos()

# poster e nota ficam no banco, mas nao entram na busca
conn = sqlite3.connect("filmes.db")
extras = {(i, t): (poster, nota) for i, t, poster, nota in conn.execute(
    "SELECT id, tipo, poster, nota FROM titulos"
)}
conn.close()


@app.get("/saude")
def saude():
    return {"ok": True, "titulos": len(infos)}


@app.get("/buscar")
def rota_buscar(
    vibe: str = Query(..., min_length=2),
    tipo: str = "todos",
    excluir: str = "",  # generos separados por virgula: "Terror,Acao"
    quantos: int = Query(30, ge=1, le=50),
    metodo: str = "rerank",  # "combinado" e mais rapido (sem o LLM reordenar)
):
    if tipo not in ("todos", "filme", "serie"):
        raise HTTPException(400, "tipo precisa ser todos, filme ou serie")
    if metodo not in ("combinado", "rerank"):
        raise HTTPException(400, "metodo precisa ser combinado ou rerank")
    generos = [g for g in excluir.split(",") if g.strip()]

    try:
        resultado, reescrita, motivos = buscar_vibe(
            vibe, infos, vetores, quantos=quantos,
            tipo=None if tipo == "todos" else tipo, excluir=generos, metodo=metodo,
        )
    except Exception as erro:
        raise HTTPException(503, f"a busca falhou: {erro}")

    lista = []
    for (id, tipo_do_titulo, titulo, ano, generos_do_titulo), nota in resultado:
        poster, nota_tmdb = extras[(id, tipo_do_titulo)]
        lista.append({
            "id": id,
            "tipo": tipo_do_titulo,
            "titulo": titulo,
            "ano": ano,
            "generos": [g.strip() for g in (generos_do_titulo or "").split(",") if g.strip()],
            "poster": poster,
            "nota_tmdb": nota_tmdb,
            "similaridade": round(nota, 3),
            "motivo": motivos.get((id, tipo_do_titulo)),
        })
    return {
        "vibe": vibe,
        "entendi": (reescrita.resumo or reescrita.descricao) if reescrita else None,
        "resultados": lista,
    }
