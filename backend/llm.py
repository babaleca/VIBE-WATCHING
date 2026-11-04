import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

# cada chamada desiste depois disso (ms); modelo ocupado as vezes fica pendurado por minutos
TIMEOUT_MS = 30000
client = genai.Client(http_options=types.HttpOptions(timeout=TIMEOUT_MS))

# se o primeiro modelo estiver ocupado ou sem cota, tenta o proximo.
# cada modelo tem a sua propria cota diaria gratis; nome que nao existe na conta
# da erro 404 e e pulado sozinho
MODELOS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

# quantas rodadas de tentativas (com espera entre elas). the evaluation script uses 4 (patient);
# a API usa 1, porque uma tela nao pode ficar minutos esperando
RODADAS = 4

# tempo maximo (s) de uma chamada a gerar(), somando todos os modelos tentados (None = sem limite)
TEMPO_MAXIMO = None

# depois de uma falha geral, quantos segundos nem tenta de novo (a API usa 60)
PAUSA_SEGUNDOS = 0
pausado_ate = 0

# modelos que nao servem mais nessa execucao (limite diario acabou ou nao existem)
fora = set()


def _falhar(mensagem):
    global pausado_ate
    pausado_ate = time.time() + PAUSA_SEGUNDOS
    raise RuntimeError(mensagem)


def gerar(contents, config=None):
    if time.time() < pausado_ate:
        raise RuntimeError("o LLM esta indisponivel agora, nem tentei de novo (pausa curta)")

    prazo = time.time() + TEMPO_MAXIMO if TEMPO_MAXIMO else None
    for rodada in range(RODADAS):
        disponiveis = [m for m in MODELOS if m not in fora]
        if not disponiveis:
            _falhar("o limite gratis do dia acabou em todos os modelos, tenta amanha")
        for modelo in disponiveis:
            if prazo and time.time() > prazo:
                _falhar("o LLM demorou demais, seguindo sem ele")
            try:
                return client.models.generate_content(model=modelo, contents=contents, config=config)
            except errors.ServerError:
                print(f"{modelo} ocupado, tentando outro modelo")
            except errors.ClientError as erro:
                if erro.code == 404:
                    print(f"{modelo} nao existe na sua conta, pulando")
                    fora.add(modelo)
                elif erro.code == 429 and "PerDay" in str(erro):
                    # limite do DIA: esperar nao adianta, so amanha
                    print(f"{modelo} bateu o limite diario gratis, pulando")
                    fora.add(modelo)
                elif erro.code == 429:
                    # limite por minuto: passa daqui a pouco
                    print(f"{modelo} no limite por minuto, tentando outro modelo")
                else:
                    raise
            except Exception as erro:
                # demorou demais (timeout) ou a conexao caiu
                print(f"{modelo} nao respondeu ({type(erro).__name__}), tentando outro modelo")
        if all(m in fora for m in MODELOS):
            _falhar("o limite gratis do dia acabou em todos os modelos, tenta amanha")
        if rodada < RODADAS - 1:
            espera = 15 * (rodada + 1)
            print(f"todos ocupados, esperando {espera}s")
            time.sleep(espera)
    _falhar("os modelos continuam indisponiveis, tenta mais tarde")
