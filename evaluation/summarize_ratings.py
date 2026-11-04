# junta os arquivos de respostas e mostra quantos resultados "cabem" em cada vibe
# uso: python -m evaluation.summarize_ratings respostas-maria.json respostas-joao.json
import sys
import json


def main():
    if len(sys.argv) < 2:
        print("uso: python -m evaluation.summarize_ratings respostas-*.json")
        return

    por_vibe = {}  # vibe -> [quantos marcaram "cabe", quantos marcaram ao todo]
    for caminho in sys.argv[1:]:
        with open(caminho, encoding="utf-8") as arq:
            dados = json.load(arq)
        print(f"{caminho}: avaliador {dados['avaliador']}, metodo {dados['metodo']}")
        for bloco in dados["vibes"]:
            marcados = [i for i in bloco["itens"] if i["cabe"] is not None]
            sim = sum(1 for i in marcados if i["cabe"])
            conta = por_vibe.setdefault(bloco["vibe"], [0, 0])
            conta[0] += sim
            conta[1] += len(marcados)

    print()
    print(f"{'vibe':40} cabem   %")
    total_sim = total = 0
    for vibe, (sim, marcados) in por_vibe.items():
        pct = 100 * sim / marcados if marcados else 0
        print(f"{vibe[:38]:40} {sim:>2}/{marcados:<3} {pct:4.0f}%")
        total_sim += sim
        total += marcados
    print("-" * 56)
    if total:
        print(f"{'TOTAL':40} {total_sim:>2}/{total:<3} {100 * total_sim / total:4.0f}%")
    print("\nobs: conta so o que foi marcado; titulos pulados ficam de fora.")


if __name__ == "__main__":
    main()
