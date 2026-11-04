import sys
import time
import sqlite3
from backend.tmdb import CAMPOS, pedir, baixar_e_salvar


def main(tipo, paginas):
    rota = CAMPOS[tipo]["rota"]
    conn = sqlite3.connect("filmes.db")
    # ids que ja estao no banco, pra nao baixar de novo
    ja_salvos = {l[0] for l in conn.execute("SELECT id FROM titulos WHERE tipo = ?", (tipo,))}

    for pagina in range(1, paginas + 1):
        # lista dos mais votados
        lista = pedir(f"/discover/{rota}", sort_by="vote_count.desc", page=pagina)
        for item in lista["results"]:
            if item["id"] in ja_salvos:
                continue
            baixar_e_salvar(conn, tipo, item["id"])
            time.sleep(0.05)  # pausa pra nao sobrecarregar a API
        conn.commit()
        print("pagina", pagina, "ok")

    total = conn.execute("SELECT COUNT(*) FROM titulos WHERE tipo = ?", (tipo,)).fetchone()[0]
    print(f"{tipo}: {total} salvos")
    conn.close()


if __name__ == "__main__":
    # uso: python -m scripts.download_titles serie 25
    if len(sys.argv) != 3 or sys.argv[1] not in CAMPOS:
        print("uso: python -m scripts.download_titles filme|serie numero_de_paginas")
    else:
        main(sys.argv[1], int(sys.argv[2]))
