import argparse
import json
from buscar import carregar_titulos, buscar_vibe

TOP = 10  # quantos resultados olhar em cada busca
TODOS_METODOS = ["puro", "reescrito", "combinado", "rerank"]
PADRAO = ["puro", "combinado", "rerank"]  # "reescrito" gasta cota e perdeu nas listas que medi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detalhes", action="store_true")  # mostra os resultados de cada busca
    parser.add_argument("--lista", default="lista_ouro.json")  # qual lista de titulos esperados
    parser.add_argument("--metodos", nargs="+", choices=TODOS_METODOS, default=PADRAO)
    args = parser.parse_args()
    METODOS = args.metodos

    with open(args.lista, encoding="utf-8") as arq:
        ouro = json.load(arq)

    infos, vetores = carregar_titulos()
    com_vetor = {(info[0], info[1]) for info in infos}

    # resultados[metodo][vibe] = (achados, esperados), ou None se o LLM falhou
    resultados = {m: {} for m in METODOS}
    for metodo in METODOS:
        for vibe, titulos in ouro.items():
            # so conta os titulos que ja tem embedding
            esperados = {(t["id"], t.get("tipo", "filme")) for t in titulos} & com_vetor

            resultado, reescrita, motivos = buscar_vibe(vibe, infos, vetores, quantos=TOP, metodo=metodo)

            # se o LLM falhou, a busca caiu pra ordem normal: esse resultado nao vale
            falhou = (metodo != "puro" and reescrita is None) or (metodo == "rerank" and not motivos)
            if falhou:
                print(f"AVISO: '{vibe}' no metodo {metodo} nao teve o LLM (nao conta)")
                resultados[metodo][vibe] = None
                continue

            achados = [i for i, nota in resultado if (i[0], i[1]) in esperados]
            resultados[metodo][vibe] = (len(achados), len(esperados))

            if args.detalhes:
                print(f"\n== {vibe} [{metodo}]: achou {len(achados)} de {len(esperados)}")
                for info, nota in resultado:
                    marca = "*" if (info[0], info[1]) in esperados else " "
                    print(f" {marca} {nota:.3f}  {info[2]} ({info[3]}) [{info[1]}]")
                    if (info[0], info[1]) in motivos:
                        print(f"         {motivos[(info[0], info[1])]}")

    # tabela final: quantos dos titulos esperados apareceram no top 10
    print(f"\nquantos dos titulos esperados apareceram no top {TOP}:\n")
    print(f"{'vibe':30s}" + "".join(f"{m:>12s}" for m in METODOS))
    for vibe in ouro:
        linha = f"{vibe[:28]:30s}"
        for m in METODOS:
            celula = resultados[m][vibe]
            texto = "n/d" if celula is None else f"{celula[0]}/{celula[1]}"
            linha += f"{texto:>12s}"
        print(linha)

    # o total so soma as vibes que deram certo em TODOS os metodos, pra comparar justo
    validas = [v for v in ouro if all(resultados[m][v] is not None for m in METODOS)]
    print("-" * (30 + 12 * len(METODOS)))
    linha = f"{'TOTAL':30s}"
    for m in METODOS:
        achados = sum(resultados[m][v][0] for v in validas)
        esperados = sum(resultados[m][v][1] for v in validas)
        linha += f"{f'{achados}/{esperados}':>12s}"
    print(linha)
    if len(validas) < len(ouro):
        print(f"(total conta so {len(validas)} de {len(ouro)} vibes: as outras tiveram falha do LLM)")


main()
