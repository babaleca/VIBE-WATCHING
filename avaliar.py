import json
from buscar import carregar_titulos, buscar

TOP = 10  # quantos resultados olhar em cada busca


def main():
    with open("lista_ouro.json", encoding="utf-8") as arq:
        ouro = json.load(arq)

    infos, vetores = carregar_titulos()
    com_vetor = {(info[0], info[1]) for info in infos}

    total_achados = 0
    total_esperados = 0
    for vibe, titulos in ouro.items():
        # so conta os titulos que ja tem embedding
        esperados = {(t["id"], t.get("tipo", "filme")) for t in titulos}
        esperados = esperados & com_vetor
        sem_vetor = len(titulos) - len(esperados)

        resultado = buscar(vibe, infos, vetores, quantos=TOP)
        achados = [info for info, nota in resultado if (info[0], info[1]) in esperados]

        print(f"\n== {vibe}")
        print(f"achou {len(achados)} de {len(esperados)} no top {TOP}"
              f" ({sem_vetor} da lista ainda sem embedding)")
        for info, nota in resultado:
            marca = "*" if (info[0], info[1]) in esperados else " "
            print(f" {marca} {nota:.3f}  {info[2]} ({info[3]}) [{info[1]}]")

        total_achados += len(achados)
        total_esperados += len(esperados)

    print(f"\ntotal: {total_achados} de {total_esperados}")


main()
