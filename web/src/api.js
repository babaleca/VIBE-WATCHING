// conversa com a API do Python (api.py)
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// as capas vem direto do TMDB: so precisamos do final do endereco, que esta no banco
export const CAPA = 'https://image.tmdb.org/t/p/w185'

export async function buscarVibe({ vibe, tipo, excluidos }) {
  const params = new URLSearchParams({
    vibe,
    tipo,
    excluir: excluidos.join(','),
    quantos: '30',
  })

  let resposta
  try {
    resposta = await fetch(`${API}/buscar?${params}`, {
      signal: AbortSignal.timeout(90000), // nao fica esperando pra sempre
    })
  } catch (e) {
    if (e.name === 'TimeoutError') {
      throw new Error('The search took too long. Try again in a minute.')
    }
    throw new Error(
      'Could not reach the API. Is it running? (uvicorn api:app --port 8000)'
    )
  }

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.detail || 'The search failed.')
  }
  return resposta.json()
}
