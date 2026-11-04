import os
import json
import time
import sqlite3
from tmdb import pedir, no_banco, baixar_e_salvar


def escolher(nome):
    # busca o nome (filme ou serie) e deixa voce escolher um ou mais
    resultados = pedir("/search/multi", query=nome)["results"]
    candidatos = [r for r in resultados if r["media_type"] in ("movie", "tv")][:4]
    if not candidatos:
        print("  nada encontrado")
        return []

    for i, c in enumerate(candidatos, 1):
        tipo = "filme" if c["media_type"] == "movie" else "serie"
        titulo = c.get("title") or c.get("name")
        data = c.get("release_date") or c.get("first_air_date") or ""
        print(f"  {i}. {titulo} ({data[:4]}) [{tipo}]")

    resp = input("  quais? (numeros separados por espaco, t = todos, 0 = pular): ")
    if resp.strip().lower() == "t":
        escolhidos = candidatos
    else:
        escolhidos = []
        for p in resp.split():
            if p.isdigit() and 1 <= int(p) <= len(candidatos):
                escolhidos.append(candidatos[int(p) - 1])

    saida = []
    for c in escolhidos:
        tipo = "filme" if c["media_type"] == "movie" else "serie"
        saida.append({"id": c["id"], "tipo": tipo, "titulo": c.get("title") or c.get("name")})
    return saida


def main():
    with open("vibes.json", encoding="utf-8") as arq:
        vibes = json.load(arq)

    # se ja existe uma lista ouro, continua dela
    ouro = {}
    if os.path.exists("lista_ouro.json"):
        with open("lista_ouro.json", encoding="utf-8") as arq:
            ouro = json.load(arq)

    conn = sqlite3.connect("filmes.db")
    for vibe, nomes in vibes.items():
        print("\n==", vibe)
        lista = ouro.setdefault(vibe, [])
        ja_tem = {(t["id"], t.get("tipo", "filme")) for t in lista}
        for nome in nomes:
            print(nome)
            for t in escolher(nome):
                if not no_banco(conn, t["tipo"], t["id"]):
                    # ainda nao esta no banco, baixa os detalhes
                    baixar_e_salvar(conn, t["tipo"], t["id"])
                    conn.commit()
                    time.sleep(0.05)
                if (t["id"], t["tipo"]) not in ja_tem:
                    lista.append(t)
                    ja_tem.add((t["id"], t["tipo"]))

    with open("lista_ouro.json", "w", encoding="utf-8") as arq:
        json.dump(ouro, arq, ensure_ascii=False, indent=2)
    print("\nlista salva em lista_ouro.json")
    conn.close()


main()
