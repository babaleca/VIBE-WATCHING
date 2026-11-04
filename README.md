# Vibe Watching

Busca de filmes e séries por vibe, não por título ou gênero. Em vez de procurar "terror" ou "comédia", você escreve algo como "cozy witchy" ou "spooky fun halloween" e o programa traz os títulos com esse clima.

Projeto em andamento.

## Por que eu fiz isso

Eu sempre quero assistir algo com um sentimento bem específico e nunca acho. O mais perto que eu conseguia era procurar listas de outras pessoas no Letterboxd, tentando palavras diferentes até achar alguém que pensou na mesma vibe que eu. Além disso, o Letterboxd só tem filmes, e pra mim "cozy" pode ser Practical Magic ou Gilmore Girls. Aqui filmes e séries entram na mesma busca, com um filtro pra escolher só um dos dois.

## Como funciona

1. Baixa os filmes e séries mais votados do TMDB (sinopse, gêneros e palavras-chave) e guarda num banco SQLite.
2. Transforma o texto de cada título em um embedding, que é uma lista de números que representa o significado do texto (uso o Gemini pra isso).
3. Transforma a busca em embedding também e calcula a similaridade do cosseno com cada título.
4. Mostra os títulos mais próximos.

## Como eu sei se está bom

Montei uma lista de referência com vibes e títulos que eu sei que combinam com cada uma (é o meu gosto, então só eu poderia fazer). O `avaliar.py` roda a busca de cada vibe e conta quantos desses títulos aparecem no top 10. Assim eu consigo comparar uma versão da busca com outra com um número, em vez de só olhar os resultados.

## O que eu descobri até agora

* A busca por embedding acha títulos pelo assunto, não pelo clima. Com "cozy witchy" apareceram filmes de terror sobre bruxas, que são o oposto de aconchegante.
* O conjunto dos mais votados deixa de fora muita coisa de nicho. Só 10 dos 24 filmes da minha primeira lista de referência estavam nos 1000 que eu tinha baixado.
* Embedding não entende negação: escrever "sem terror" na busca puxa mais terror.

## Próximos passos

* Reordenar os resultados com um LLM que lê cada título e decide se tem a vibe
* Reescrever a busca com um LLM antes de gerar o embedding
* Gerar tags de vibe de cada título com LLM e comparar com a versão atual
* Interface web

## Como rodar

Precisa de Python, uma chave de API do TMDB e uma chave do Gemini.

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com:

```
TMDB_API_KEY=sua_chave
GEMINI_API_KEY=sua_chave
```

Depois:

```
python baixar_titulos.py filme 50
python baixar_titulos.py serie 25
python gerar_embeddings.py
python buscar.py "cozy witchy"
python buscar.py "cozy" --tipo serie
```

O banco (`filmes.db`) não está no repositório, ele é criado quando você roda os scripts.

## Créditos

This product uses the TMDB API but is not endorsed or certified by TMDB.

Os dados de filmes e séries vêm do [TMDB](https://www.themoviedb.org/).
