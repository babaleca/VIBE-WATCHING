import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()  # acha a GEMINI_API_KEY sozinho

# o nome do modelo pode vir do terminal: python testar_llm.py nome-do-modelo
modelo = sys.argv[1] if len(sys.argv) > 1 else "gemini-flash-latest"

# testa o modelo que escreve texto (nao e o de embedding)
res = client.models.generate_content(
    model=modelo,
    contents="Responda em uma frase: o que significa 'cozy witchy'?",
)
print(res.text)
