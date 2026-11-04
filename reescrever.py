import sys
import json
import os
from pydantic import BaseModel
from google.genai import types
from llm import gerar

ARQUIVO_CACHE = "reescritas.json"


# formato que o LLM precisa devolver
class Busca(BaseModel):
    descricao: str  # usada na busca (portugues, porque as sinopses do banco sao em portugues)
    excluir_generos: list[str]
    leituras: list[str]  # outras interpretacoes possiveis, so quando o pedido e ambiguo
    resumo: str  # frase curta em ingles pra mostrar na tela


INSTRUCAO = """Voce ajuda a buscar filmes e series pela vibe (clima e sentimento).
O pedido pode estar em qualquer idioma: entenda o pedido e responda nos idiomas indicados abaixo.
Receba o pedido da pessoa e devolva:
- descricao: 2 frases em portugues descrevendo o clima e o tipo de historia que combina com o pedido. Fale so do que a pessoa quer, nunca use negacao como "sem terror".
- excluir_generos: generos que quase certamente nao combinam com o pedido. Use so nomes de generos em portugues, como Terror, Acao, Guerra, Crime, Thriller. Se nao tiver certeza, deixe a lista vazia.
- leituras: se o pedido for curto ou ambiguo (uma palavra com varios sentidos, por exemplo "irmandade" pode ser amizade entre mulheres, irmaos homens ou ordem religiosa), escreva de 2 a 3 frases curtas em portugues, uma para cada leitura DIFERENTE possivel. Se o pedido for claro, deixe a lista vazia.
- resumo: uma frase curta em ingles, falando direto com a pessoa (\"You want...\", \"You're after...\"), dizendo como voce entendeu o pedido. Nunca escreva \"the user\". Se deu varias leituras, cite-as rapidamente."""


def ler_cache():
    # le o arquivo com as reescritas que ja foram feitas
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def reescrever(busca):
    # se essa vibe ja foi reescrita antes, usa o resultado salvo
    # (o "v2:" separa das reescritas antigas, que nao tinham leituras nem resumo)
    cache = ler_cache()
    chave = "v2:" + busca.strip().lower()
    if chave in cache:
        return Busca(**cache[chave])

    # senao, pergunta pro LLM e salva a resposta
    res = gerar(
        busca,
        types.GenerateContentConfig(
            system_instruction=INSTRUCAO,
            response_mime_type="application/json",
            response_schema=Busca,
        ),
    )
    cache[chave] = res.parsed.model_dump()
    with open(ARQUIVO_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    return res.parsed


if __name__ == "__main__":
    resultado = reescrever(" ".join(sys.argv[1:]))
    print("descricao:", resultado.descricao)
    print("excluir:", resultado.excluir_generos)
    print("leituras:", resultado.leituras)
    print("resumo:", resultado.resumo)
