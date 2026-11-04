// efeitos sonoros 8-bit, feitos na hora com o Web Audio (nenhum arquivo de audio)
// cada som e uma ou mais "notas": uma onda (quadrada, triangular...) que muda de
// frequencia e some aos poucos. o ruido imita barulhos tipo papel e riscado.

let contexto = null
let ligado = true
let bufferRuido = null

try {
  ligado = localStorage.getItem('som') !== 'off'
} catch {
  // sem localStorage: segue ligado
}

function audio() {
  if (!contexto) {
    const Contexto = window.AudioContext || window.webkitAudioContext
    if (!Contexto) return null
    contexto = new Contexto()
  }
  // navegadores so liberam som depois de um clique da pessoa
  if (contexto.state === 'suspended') contexto.resume()
  return contexto
}

// uma nota: onda que vai da frequencia "de" ate "ate" e vai sumindo
function nota({ tipo = 'square', de, ate, dur = 0.1, vol = 0.07, atraso = 0 }) {
  if (!ligado) return
  const c = audio()
  if (!c) return
  const t = c.currentTime + atraso
  const osc = c.createOscillator()
  const ganho = c.createGain()
  osc.type = tipo
  osc.frequency.setValueAtTime(de, t)
  if (ate) osc.frequency.exponentialRampToValueAtTime(ate, t + dur)
  ganho.gain.setValueAtTime(vol, t)
  ganho.gain.exponentialRampToValueAtTime(0.0001, t + dur)
  osc.connect(ganho).connect(c.destination)
  osc.start(t)
  osc.stop(t + dur + 0.02)
}

// ruido filtrado: a frequencia do filtro pode "varrer" de um valor pra outro
function ruido({ de, ate, dur = 0.08, vol = 0.08, atraso = 0 }) {
  if (!ligado) return
  const c = audio()
  if (!c) return
  if (!bufferRuido) {
    bufferRuido = c.createBuffer(1, c.sampleRate, c.sampleRate)
    const dados = bufferRuido.getChannelData(0)
    for (let i = 0; i < dados.length; i++) dados[i] = Math.random() * 2 - 1
  }
  const t = c.currentTime + atraso
  const fonte = c.createBufferSource()
  fonte.buffer = bufferRuido
  const filtro = c.createBiquadFilter()
  filtro.type = 'bandpass'
  filtro.Q.value = 1.2
  filtro.frequency.setValueAtTime(de, t)
  if (ate) filtro.frequency.exponentialRampToValueAtTime(ate, t + dur)
  const ganho = c.createGain()
  ganho.gain.setValueAtTime(vol, t)
  ganho.gain.exponentialRampToValueAtTime(0.0001, t + dur)
  fonte.connect(filtro).connect(ganho).connect(c.destination)
  fonte.start(t)
  fonte.stop(t + dur + 0.02)
}

// ---------- liga e desliga ----------
export function somLigado() {
  return ligado
}

export function alternarSom() {
  ligado = !ligado
  try {
    localStorage.setItem('som', ligado ? 'on' : 'off')
  } catch {
    // tudo bem se nao salvar
  }
  if (ligado) clique()
  return ligado
}

// ---------- botoes e filtros ----------
export function clique() {
  nota({ de: 660, ate: 880, dur: 0.06 })
}

export function sugestao() {
  nota({ de: 880, ate: 1320, dur: 0.09, vol: 0.06 })
  nota({ de: 1320, dur: 0.07, vol: 0.04, atraso: 0.07 })
}

export function buscar() {
  nota({ de: 523, dur: 0.07 })
  nota({ de: 659, dur: 0.07, atraso: 0.07 })
  nota({ de: 784, dur: 0.12, atraso: 0.14 })
}

export function riscarGenero() {
  ruido({ de: 3500, ate: 1500, dur: 0.14, vol: 0.09 })
  nota({ de: 190, ate: 100, dur: 0.14, vol: 0.06 })
}

export function desriscarGenero() {
  nota({ de: 400, ate: 700, dur: 0.08 })
}

// ---------- estante e cestinha ----------
export function naCesta() {
  // whoosh do filme saindo da estante
  ruido({ de: 500, ate: 2200, dur: 0.13, vol: 0.07 })
  // toc dele caindo na cesta
  nota({ tipo: 'triangle', de: 160, ate: 60, dur: 0.12, vol: 0.14, atraso: 0.12 })
  // e o ding de moedinha
  nota({ de: 784, dur: 0.07, vol: 0.05, atraso: 0.16 })
  nota({ de: 1175, dur: 0.16, vol: 0.05, atraso: 0.23 })
}

export function devolver() {
  ruido({ de: 1800, ate: 400, dur: 0.12, vol: 0.06 })
  nota({ de: 600, ate: 380, dur: 0.1, atraso: 0.05 })
  nota({ tipo: 'triangle', de: 140, ate: 70, dur: 0.1, vol: 0.1, atraso: 0.12 })
}

// ---------- recibo ----------
export function abrirRecibo() {
  // maquininha ligando
  nota({ tipo: 'sawtooth', de: 120, ate: 520, dur: 0.25, vol: 0.05 })
  nota({ de: 880, dur: 0.08, vol: 0.05, atraso: 0.27 })
}

// um "tique" de impressora
function tiqueImpressora() {
  ruido({ de: 3800, dur: 0.03, vol: 0.08 })
  nota({ de: 150, dur: 0.035, vol: 0.04 })
}

// toca os tiques enquanto imprime; devolve uma funcao que para tudo
export function imprimir(segundos, passos) {
  const intervalo = (segundos * 1000) / passos
  const id = setInterval(tiqueImpressora, intervalo)
  tiqueImpressora()
  return () => clearInterval(id)
}

export function pronto() {
  // sininho de balcao
  nota({ tipo: 'sine', de: 1318, dur: 0.7, vol: 0.12 })
  nota({ tipo: 'sine', de: 1760, dur: 0.9, vol: 0.09, atraso: 0.04 })
}

export function baixar() {
  ;[523, 659, 784, 1047].forEach((f, i) =>
    nota({ de: f, dur: 0.08, vol: 0.06, atraso: i * 0.06 })
  )
}

export function fechar() {
  nota({ de: 520, ate: 260, dur: 0.1 })
}
