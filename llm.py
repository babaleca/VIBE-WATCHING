import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client()
MODELO = "gemini-flash-latest"


def gerar(contents, config=None):
    # chama o LLM; se o servidor estiver ocupado (503), espera e tenta de novo
    for tentativa in range(6):
        try:
            return client.models.generate_content(model=MODELO, contents=contents, config=config)
        except errors.ServerError:
            espera = 10 * (tentativa + 1)
            print(f"servidor ocupado, tentando de novo em {espera}s")
            time.sleep(espera)
    raise RuntimeError("o modelo continua indisponivel, tenta mais tarde")
