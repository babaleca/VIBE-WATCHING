import { useRef, useState } from 'react'
import '@fontsource/press-start-2p'
import '@fontsource/vt323'
import './App.css'
import Estante from './componentes/Estante'
import Cestinha from './componentes/Cestinha'
import Recibo from './componentes/Recibo'
import * as sons from './sons'
import { buscarVibe } from './api'

const TIPOS = [
  { valor: 'todos', nome: 'Movies & series' },
  { valor: 'filme', nome: 'Movies' },
  { valor: 'serie', nome: 'Series' },
]

// chave = nome do genero no banco (portugues, e o que a API entende); rotulo = o que aparece na tela
const GENEROS = [
  { chave: 'Ação', rotulo: 'Action' },
  { chave: 'Aventura', rotulo: 'Adventure' },
  { chave: 'Animação', rotulo: 'Animation' },
  { chave: 'Comédia', rotulo: 'Comedy' },
  { chave: 'Crime', rotulo: 'Crime' },
  { chave: 'Documentário', rotulo: 'Documentary' },
  { chave: 'Drama', rotulo: 'Drama' },
  { chave: 'Família', rotulo: 'Family' },
  { chave: 'Fantasia', rotulo: 'Fantasy' },
  { chave: 'História', rotulo: 'History' },
  { chave: 'Terror', rotulo: 'Horror' },
  { chave: 'Música', rotulo: 'Music' },
  { chave: 'Mistério', rotulo: 'Mystery' },
  { chave: 'Romance', rotulo: 'Romance' },
  { chave: 'Ficção científica', rotulo: 'Science fiction' },
  { chave: 'Thriller', rotulo: 'Thriller' },
  { chave: 'Guerra', rotulo: 'War' },
]

// vibes prontas: clicou, preenche o campo
const SUGESTOES = [
  { icone: '🍂', texto: 'autumn feelings' },
  { icone: '👑', texto: 'rococo extravagance' },
  { icone: '🥀', texto: 'pretty on the outside, rotten inside' },
]

function App() {
  // cada coisa que muda na tela vira um estado
  const [vibe, setVibe] = useState('')
  const [tipo, setTipo] = useState('todos')
  const [excluidos, setExcluidos] = useState([])
  const [resultados, setResultados] = useState([])
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)
  const [entendi, setEntendi] = useState(null) // como o LLM entendeu a vibe
  const [buscou, setBuscou] = useState(false)
  const [vibeBuscada, setVibeBuscada] = useState('') // a vibe da ultima busca feita
  const [cesta, setCesta] = useState([])
  const [reciboAberto, setReciboAberto] = useState(false)
  const [som, setSom] = useState(sons.somLigado())
  const voando = useRef(new Set()) // caixas que estao no meio do voo

  // liga e desliga um genero da lista de excluidos
  function alternarGenero(genero) {
    if (excluidos.includes(genero)) {
      sons.desriscarGenero()
      setExcluidos(excluidos.filter((g) => g !== genero))
    } else {
      sons.riscarGenero()
      setExcluidos([...excluidos, genero])
    }
  }

  async function buscar(evento) {
    evento.preventDefault() // não deixa a página recarregar
    if (vibe.trim().length < 2 || carregando) return

    sons.buscar()
    setCarregando(true)
    setErro(null)
    try {
      const dados = await buscarVibe({ vibe: vibe.trim(), tipo, excluidos })
      setResultados(dados.resultados)
      setEntendi(dados.entendi)
      setBuscou(true)
      setVibeBuscada(vibe.trim())
    } catch (e) {
      setErro(e.message)
    }
    setCarregando(false)
  }

  // mesmo id pode existir como filme e como serie, entao compara os dois
  function mesmoTitulo(a, b) {
    return a.id === b.id && a.tipo === b.tipo
  }

  function colocarNaCesta(titulo, elemento) {
    const chave = titulo.id + titulo.tipo
    if (voando.current.has(chave)) return // ja esta voando, ignora o segundo clique
    const alvo = document.querySelector('.cesta')
    const reduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    // cada filme guarda a vibe com que foi encontrado
    const novo = { ...titulo, vibe: vibeBuscada }
    const guardar = () => {
      voando.current.delete(chave)
      sons.naCesta()
      setCesta((atual) => [...atual, novo])
    }

    if (!elemento || !alvo || reduzido) {
      guardar()
      return
    }

    voando.current.add(chave)
    const de = elemento.getBoundingClientRect()
    const para = alvo.getBoundingClientRect()

    // copia da caixa que voa por cima de tudo
    const copia = elemento.cloneNode(true)
    copia.classList.remove('com-hover')
    Object.assign(copia.style, {
      position: 'fixed',
      left: de.left + 'px',
      top: de.top + 'px',
      width: de.width + 'px',
      height: de.height + 'px',
      margin: '0',
      zIndex: '1000',
      pointerEvents: 'none',
      transform: 'none',
    })
    document.body.appendChild(copia)
    elemento.style.visibility = 'hidden' // some da estante enquanto voa

    // vai ate o meio da cesta, diminuindo e girando um pouquinho
    const dx = para.left + para.width / 2 - (de.left + de.width / 2)
    const dy = para.top + para.height * 0.4 - (de.top + de.height / 2)
    const voo = copia.animate(
      [
        { transform: 'translate(0, 0) scale(1) rotate(0deg)', offset: 0 },
        { transform: `translate(${dx * 0.5}px, ${dy * 0.5 - 70}px) scale(0.85) rotate(-8deg)`, offset: 0.5 },
        { transform: `translate(${dx}px, ${dy}px) scale(0.5) rotate(6deg)`, offset: 1 },
      ],
      { duration: 480, easing: 'ease-in' }
    )
    voo.onfinish = () => {
      copia.remove()
      guardar()
    }
  }

  function devolverPraEstante(titulo) {
    sons.devolver()
    setCesta(cesta.filter((t) => !mesmoTitulo(t, titulo)))
  }

  // a estante mostra o que a busca trouxe e que NAO esta na cesta
  // (os filtros de tipo e genero ja foram aplicados pela API)
  const naEstante = resultados.filter(
    (r) => !cesta.some((c) => mesmoTitulo(c, r))
  )

  return (
    <main className="pagina">
      <button
        type="button"
        className="botao-som"
        onClick={() => setSom(sons.alternarSom())}
      >
        SOUND: {som ? 'ON' : 'OFF'}
      </button>

      <header className="letreiro">
        <h1>VIBE WATCHING</h1>
        <p>find movies and series with a vibe you like</p>
      </header>

      <div className="tela">
        <Estante
          titulos={naEstante}
          aoEscolher={colocarNaCesta}
          carregando={carregando}
          buscou={buscou}
        />

        <div className="centro">
          <form className="caixa" onSubmit={buscar}>
            <h2 className="titulo-secao">WHAT'S THE VIBE?</h2>
            <div className="campo">
              <input
                value={vibe}
                onChange={(e) => setVibe(e.target.value)}
                placeholder='try "cozy witchy" (any language works)'
              />
              <button className="botao" type="submit" disabled={carregando}>
                {carregando ? 'SEARCHING' : 'SEARCH'}
              </button>
            </div>

            <div className="filtros">
              <div>
                <h3 className="titulo-secao">I WANT</h3>
                <div className="grupo">
                  {TIPOS.map((t) => (
                    <button
                      type="button"
                      key={t.valor}
                      className={
                        'etiqueta' + (tipo === t.valor ? ' ligada' : '')
                      }
                      onClick={() => {
                        sons.clique()
                        setTipo(t.valor)
                      }}
                    >
                      {t.nome}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="titulo-secao">SKIP THESE GENRES</h3>
                <div className="grupo">
                  {GENEROS.map((g) => (
                    <button
                      type="button"
                      key={g.chave}
                      className={
                        'etiqueta' +
                        (excluidos.includes(g.chave) ? ' excluida' : '')
                      }
                      onClick={() => alternarGenero(g.chave)}
                    >
                      {g.rotulo}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </form>

          {erro && <div className="aviso-erro">{erro}</div>}

          {entendi && !erro && (
            <div className="entendi">
              <h3 className="titulo-secao">HOW I UNDERSTOOD IT</h3>
              <p>{entendi}</p>
            </div>
          )}

          <section>
            <h2 className="titulo-secao">NEED AN IDEA?</h2>
            <div className="sugestoes">
              {SUGESTOES.map((s) => (
                <button
                  type="button"
                  key={s.texto}
                  className="sugestao"
                  onClick={() => {
                    sons.sugestao()
                    setVibe(s.texto)
                  }}
                >
                  <span className="icone">{s.icone}</span>
                  {s.texto}
                </button>
              ))}
            </div>
          </section>
        </div>

        <Cestinha
          itens={cesta}
          aoDevolver={devolverPraEstante}
          aoFinalizar={() => {
            sons.abrirRecibo()
            setReciboAberto(true)
          }}
        />
      </div>

      <footer className="creditos">
        Data and covers from{' '}
        <a href="https://www.themoviedb.org" target="_blank" rel="noreferrer">
          TMDB
        </a>
        . This product uses the TMDB API but is not endorsed or certified by TMDB.
      </footer>

      {reciboAberto && (
        <Recibo
          itens={cesta}
          aoFechar={() => {
            sons.fechar()
            setReciboAberto(false)
          }}
        />
      )}
    </main>
  )
}

export default App
