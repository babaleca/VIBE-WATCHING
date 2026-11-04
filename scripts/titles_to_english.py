from concurrent.futures import ThreadPoolExecutor
import shutil
import sqlite3
from backend import tmdb

# troca so o NOME e o POSTER de cada titulo pelas versoes em ingles.
# os vetores (embeddings) continuam os mesmos, entao nao gasta cota do Gemini.


def buscar_ingles(item):
    id, tipo = item
    rota = tmdb.CAMPOS[tipo]["rota"]
    campo = tmdb.CAMPOS[tipo]["titulo"]
    try:
        # o pedir() do tmdb.py fixa pt-BR, entao aqui e feito o pedido direto em ingles
        r = tmdb.sessao.get(
            f"{tmdb.BASE}/{rota}/{id}",
            params={"api_key": tmdb.CHAVE, "language": "en-US"},
            timeout=30,
        )
        r.raise_for_status()
        dados = r.json()
        return id, tipo, dados.get(campo), dados.get("poster_path")
    except Exception as erro:
        print(f"falhou {tipo} {id}: {erro}")
        return id, tipo, None, None


def main():
    shutil.copy("filmes.db", "filmes_backup_pt.db")  # copia de seguranca
    print("backup salvo em filmes_backup_pt.db")

    conn = sqlite3.connect("filmes.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS titulos_en (id INTEGER, tipo TEXT, titulo TEXT, poster TEXT, PRIMARY KEY (id, tipo))"
    )
    feitos = {(i, t) for i, t in conn.execute("SELECT id, tipo FROM titulos_en")}
    todos = conn.execute("SELECT id, tipo FROM titulos").fetchall()
    faltam = [x for x in todos if x not in feitos]
    print(f"{len(faltam)} titulos pra buscar em ingles (de {len(todos)})")

    # 8 pedidos ao mesmo tempo; a gravacao no banco fica so aqui, na thread principal
    with ThreadPoolExecutor(max_workers=8) as pool:
        for n, (id, tipo, titulo, poster) in enumerate(pool.map(buscar_ingles, faltam), start=1):
            if titulo:
                conn.execute("INSERT OR REPLACE INTO titulos_en VALUES (?, ?, ?, ?)", (id, tipo, titulo, poster))
            if n % 100 == 0:
                conn.commit()
                print(f"  {n}/{len(faltam)}")
    conn.commit()

    # aplica: nome em ingles; poster em ingles so se existir (senao mantem o atual)
    conn.execute("""
        UPDATE titulos SET
            titulo = (SELECT e.titulo FROM titulos_en e WHERE e.id = titulos.id AND e.tipo = titulos.tipo),
            poster = COALESCE(
                (SELECT e.poster FROM titulos_en e WHERE e.id = titulos.id AND e.tipo = titulos.tipo),
                poster)
        WHERE EXISTS (SELECT 1 FROM titulos_en e WHERE e.id = titulos.id AND e.tipo = titulos.tipo)
    """)
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM titulos").fetchone()[0]
    ok = conn.execute("SELECT COUNT(*) FROM titulos_en").fetchone()[0]
    print(f"pronto: {ok} de {total} titulos em ingles")
    if ok < total:
        print("alguns falharam: rode de novo que ele continua de onde parou")
    conn.close()


if __name__ == "__main__":
    main()
