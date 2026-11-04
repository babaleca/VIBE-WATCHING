# Vibe Watching

Busca de filmes e séries por vibe, não por título ou gênero. Em vez de procurar "terror" ou "comédia", você escreve algo como "cozy witchy" ou "crazy dream" e o programa traz os títulos com esse clima. A interface é uma locadora em pixel art: os resultados ficam numa estante, você coloca os escolhidos numa cestinha e no fim sai um recibo em JPEG pra baixar.

![Vibe Watching em uso](preview.gif)

Vídeo completo (38s): [demo.mp4](demo.mp4)

## Por que eu fiz isso

Eu sempre quero assistir algo com um sentimento bem específico e nunca acho. O mais perto que eu conseguia era procurar listas de outras pessoas no Letterboxd, tentando palavras diferentes até achar alguém que pensou na mesma vibe que eu. Além disso, o Letterboxd só tem filmes, e pra mim "cozy" pode ser Practical Magic ou Gilmore Girls. Aqui filmes e séries entram na mesma busca, com um filtro pra escolher só um dos dois.

## Como funciona

1. Baixa os filmes e séries mais votados do TMDB (sinopse, gêneros e palavras-chave) e guarda num banco SQLite (cerca de 1500 títulos).
2. Transforma o texto de cada título em um embedding, que é uma lista de números que representa o significado do texto (uso o Gemini pra isso).
3. Quando alguém busca, um LLM reescreve a vibe numa descrição mais clara e diz quais gêneros claramente não combinam.
4. A busca vira embedding também e é comparada (similaridade do cosseno) com todos os títulos. Os gêneros que a pessoa marcou como "sem" são removidos de verdade.
5. Os 80 mais próximos passam por um segundo LLM, que reordena e escreve uma frase explicando por que cada um combina.
6. Se o LLM falhar ou estiver ocupado, a busca cai pra ordem dos embeddings e continua funcionando.

A API é feita em FastAPI e a interface em React.

## Como eu sei se está bom

Montei uma lista de referência com vibes e títulos que eu sei que combinam com cada uma (é o meu gosto). O `avaliar.py` roda a busca de cada vibe e conta quantos desses títulos aparecem no top 10, pra eu comparar um método com outro com um número, em vez de só olhar os resultados.

Métodos comparados: `puro` (embedding da vibe como foi escrita), `reescrito` (embedding da descrição feita pelo LLM), `combinado` (vibe + descrição) e `rerank` (combinado + reordenação por LLM).

**Minha lista (38 títulos, 6 vibes)**

| puro | reescrito | combinado |
|---|---|---|
| 8/38 | 9/38 | 11/38 |

Nessa lista os títulos esperados ficam no top 50 em 23 de 38 casos e no top 100 em 31 de 38 casos (combinado).

**Lista da minha irmã (27 títulos, 7 vibes), usada só pra medir, sem ajustar nada em cima dela**

| puro | reescrito | combinado | rerank |
|---|---|---|---|
| 5/27 | 2/27 | 2/27 | 2/27 |

### Cuidados ao ler esses números

* As amostras são pequenas. Uma diferença de 2 ou 3 títulos pode ser sorte.
* A lista de referência é o gosto de uma pessoa. Se a busca devolve um título que combina com a vibe mas que não está na lista, ele não conta. Na lista da minha irmã, "Estranhamente Aconchegante" trouxe O Estranho Mundo de Jack, Amélie e Encanto, que fazem sentido, mas ela tinha escolhido Coraline, Grinch e Boxtrolls.
* Nos meus testes o rerank ficou igual ao combinado em contagem, porque ele só reordena os 50 candidatos: se o título certo não está entre eles, não adianta.

## O que eu descobri até agora

* A busca por embedding acha títulos pelo assunto, não pelo clima. Com "cozy witchy" apareceram filmes de terror sobre bruxas, que são o oposto de aconchegante.
* Reescrever a busca com um LLM ajudou na minha lista e atrapalhou na da minha irmã. Ele escolhe uma interpretação, e quando a vibe é curta ou ambígua ele pode escolher a errada.
* "Irmandade" sozinha virou terror com freiras (a busca pura entendeu como ordem religiosa) e máfia e gangues (o LLM entendeu como irmãos). Ninguém entendeu irmandade entre garotas, que era o que ela queria dizer.
* Embedding não entende negação: escrever "sem terror" na busca puxa mais terror. Por isso os gêneros que a pessoa não quer são filtrados de fora, e não escritos no texto da busca.
* O conjunto dos mais votados deixa de fora muita coisa de nicho, então alguns títulos esperados nem existem no banco.

## Limitações

* Uso o plano grátis do Gemini, que tem limite de requisições por dia. Quando o limite acaba, a busca volta pro modo sem LLM.
* Só tem os títulos que baixei do TMDB.

## Próximos passos

* Quando a vibe for ambígua, o LLM propor 2 ou 3 leituras diferentes e misturar os resultados
* Medir com outras pessoas: elas marcam quais dos 10 resultados combinam com a vibe, em vez de eu comparar com uma lista fixa
* Filtro de faixa etária
* Gerar tags de vibe de cada título com LLM e comparar com a versão atual

## Como rodar

Precisa de Python, Node, uma chave de API do TMDB e uma chave do Gemini.

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

Montar o banco e os embeddings:

```
python baixar_titulos.py filme 50
python baixar_titulos.py serie 25
python gerar_embeddings.py
```

Buscar pelo terminal:

```
python buscar.py "cozy witchy"
python buscar.py "cozy" --tipo serie --sem terror
```

Rodar a interface (dois terminais):

```
uvicorn api:app --port 8000
```

```
cd web
npm install
npm run dev
```

Avaliar a busca:

```
python avaliar.py
python avaliar.py --lista outra_lista.json --detalhes
```

O banco (`filmes.db`) e o cache dos embeddings não estão no repositório, eles são criados quando você roda os scripts.

## Créditos

Os dados e as capas de filmes e séries vêm do [TMDB](https://www.themoviedb.org/). Este produto usa a API do TMDB, mas não é endossado nem certificado por ela.
