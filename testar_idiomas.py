# mesma vibe em varios idiomas: os resultados deveriam ser parecidos
# uso: python testar_idiomas.py
from buscar import carregar_titulos, buscar_vibe

# o primeiro de cada grupo (ingles) e a referencia
VIBES = {
    "cozy witchy": [
        "cozy witchy",
        "acolhedor e bruxesco",
        "acogedor y de brujas",
        "cosy ambiance de sorcières",
        "ほっこり魔女っぽい雰囲気",
    ],
    "crazy dream": [
        "crazy dream",
        "sonho maluco",
        "sueño loco",
        "rêve fou",
        "奇妙な夢",
    ],
}


def top10(vibe, infos, vetores):
    resultado, _, _ = buscar_vibe(vibe, infos, vetores, quantos=10, metodo="combinado")
    return [(i[0], i[1]) for i, _nota in resultado], [i[2] for i, _nota in resultado]


def main():
    infos, vetores = carregar_titulos()
    for grupo, versoes in VIBES.items():
        print("\n=====", grupo)
        base_ids, base_nomes = top10(versoes[0], infos, vetores)
        print(f"{versoes[0]!r} (referencia):", ", ".join(base_nomes))
        for texto in versoes[1:]:
            ids, nomes = top10(texto, infos, vetores)
            iguais = len(set(ids) & set(base_ids))
            print(f"\n{texto!r}: {iguais}/10 iguais a referencia")
            print("   ", ", ".join(nomes))


main()
