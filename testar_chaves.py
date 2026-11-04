import os
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()  # le o .env e coloca as chaves no ambiente

# testa o TMDB
r = requests.get(
    "https://api.themoviedb.org/3/movie/popular",
    params={"api_key": os.getenv("TMDB_API_KEY"), "language": "pt-BR"},
)
print("TMDB status:", r.status_code)
print("primeiro filme:", r.json()["results"][0]["title"])

# testa o Gemini
client = genai.Client()  # acha a GEMINI_API_KEY sozinho
res = client.models.embed_content(model="gemini-embedding-001", contents="cozy witchy")
print("Gemini ok, tamanho da lista:", len(res.embeddings[0].values))
