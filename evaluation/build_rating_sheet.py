# gera uma folha em HTML pra alguem marcar quais resultados "cabem" em cada vibe
# uso: python -m evaluation.build_rating_sheet evaluation/data/vibes_sister.json [metodo] [saida.html]
# o arquivo de vibes pode ser um .json (usa as chaves) ou um .txt (uma vibe por linha)
import sys
import json
import sqlite3
from backend.search import carregar_titulos, buscar_vibe

QUANTOS = 10


def ler_vibes(caminho):
    if caminho.endswith(".json"):
        with open(caminho, encoding="utf-8") as arq:
            return list(json.load(arq).keys())
    with open(caminho, encoding="utf-8") as arq:
        return [linha.strip() for linha in arq if linha.strip()]


def main():
    caminho = sys.argv[1]
    metodo = sys.argv[2] if len(sys.argv) > 2 else "rerank"
    saida = sys.argv[3] if len(sys.argv) > 3 else "avaliacao.html"

    vibes = ler_vibes(caminho)
    infos, vetores = carregar_titulos()

    conn = sqlite3.connect("filmes.db")
    posters = {(i, t): p for i, t, p in conn.execute("SELECT id, tipo, poster FROM titulos")}
    conn.close()

    dados = {"metodo": metodo, "vibes": []}
    for vibe in vibes:
        print("buscando:", vibe)
        resultado, _, _ = buscar_vibe(vibe, infos, vetores, quantos=QUANTOS, metodo=metodo)
        itens = []
        for (id, tipo, titulo, ano, _g), _nota in resultado:
            itens.append({
                "id": id, "tipo": tipo, "titulo": titulo, "ano": ano,
                "poster": posters.get((id, tipo)), "cabe": None,
            })
        dados["vibes"].append({"vibe": vibe, "itens": itens})

    with open("evaluation/rating_sheet_template.html", encoding="utf-8") as arq:
        pagina = arq.read()
    # evita que um "</script>" dentro dos dados quebre a pagina
    texto = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    pagina = pagina.replace("__DADOS__", texto)
    with open(saida, "w", encoding="utf-8") as arq:
        arq.write(pagina)
    print("pronto:", saida)


if __name__ == "__main__":
    main()
