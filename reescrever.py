import sys
import json
import os
from pydantic import BaseModel
from google.genai import types
from llm import gerar

ARQUIVO_CACHE = "reescritas.json"


# formato que o LLM precisa devolver
class Busca(BaseModel):
    descricao: str
    excluir_generos: list[str]


INSTRUCAO = """Voce ajuda a buscar filmes e series pela vibe (clima e sentimento).
Receba o pedido da pessoa e devolva:
- descricao: 2 frases em portugues descrevendo o clima e o tipo de historia que combina com o pedido. Fale so do que a pessoa quer, nunca use negacao como "sem terror".
- excluir_generos: generos que quase certamente nao combinam com o pedido. Use so nomes de generos em portugues, como Terror, Acao, Guerra, Crime, Thriller. Se nao tiver certeza, deixe a lista vazia."""


def ler_cache():
    # le o arquivo com as reescritas que ja foram feitas
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def reescrever(busca):
    # se essa vibe ja foi reescrita antes, usa o resultado salvo
    cache = ler_cache()
    chave = busca.strip().lower()
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
