import { useState } from 'react'
import '@fontsource/press-start-2p'
import '@fontsource/vt323'
import './App.css'
import Estante from './componentes/Estante'
import Cestinha from './componentes/Cestinha'
import Recibo from './componentes/Recibo'
import * as sons from './sons'
import { RESULTADOS_FALSOS } from './dadosFalsos'

const TIPOS = [
  { valor: 'todos', nome: 'Tudo' },
  { valor: 'filme', nome: 'Filmes' },
  { valor: 'serie', nome: 'Séries' },
]

const GENEROS = [
  'Ação', 'Aventura', 'Animação', 'Comédia', 'Crime', 'Documentário',
  'Drama', 'Família', 'Fantasia', 'História', 'Terror', 'Música',
  'Mistério', 'Romance', 'Ficção científica', 'Thriller', 'Guerra',
]

// vibes prontas: clicou, preenche o campo
const SUGESTOES = [
  { icone: '📖', texto: 'baseados em clássicos da literatura' },
  { icone: '🍂', texto: 'com uma pegada outonal' },
  { icone: '🕯️', texto: 'cozy witchy' },
  { icone: '🌙', texto: 'crazy dream' },
  { icone: '🧚', texto: 'a magia existe, só precisa encontrar' },
  { icone: '👯', texto: 'girls girls girls' },
]

function App() {
  // cada coisa que muda na tela vira um estado
  const [vibe, setVibe] = useState('')
  const [tipo, setTipo] = useState('todos')
  const [excluidos, setExcluidos] = useState([])
  const [resultados] = useState(RESULTADOS_FALSOS) // depois vem da busca de verdade
  const [cesta, setCesta] = useState([])
  const [reciboAberto, setReciboAberto] = useState(false)
  const [som, setSom] = useState(sons.somLigado())

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

  function buscar(evento) {
    evento.preventDefault() // não deixa a página recarregar
    sons.buscar()
    console.log({ vibe, tipo, excluidos }) // por enquanto só mostra no console
  }

  // mesmo id pode existir como filme e como serie, entao compara os dois
  function mesmoTitulo(a, b) {
    return a.id === b.id && a.tipo === b.tipo
  }

  function colocarNaCesta(titulo) {
    sons.naCesta()
    setCesta([...cesta, titulo])
  }

  function devolverPraEstante(titulo) {
    sons.devolver()
    setCesta(cesta.filter((t) => !mesmoTitulo(t, titulo)))
  }

  // aplica os filtros: tipo (filme/serie) e generos excluidos
  const filtrados = resultados.filter((r) => {
    const tipoCerto = tipo === 'todos' || r.tipo === tipo
    const temGeneroExcluido = r.generos.some((g) => excluidos.includes(g))
    return tipoCerto && !temGeneroExcluido
  })

  // a estante mostra o que passou nos filtros e NAO esta na cesta
  const naEstante = filtrados.filter(
    (r) => !cesta.some((c) => mesmoTitulo(c, r))
  )

  return (
    <main className="pagina">
      <button
        type="button"
        className="botao-som"
        onClick={() => setSom(sons.alternarSom())}
      >
        SOM: {som ? 'LIGADO' : 'DESLIGADO'}
      </button>

      <header className="letreiro">
        <h1>VIBE WATCHING</h1>
        <p>filmes e séries pela vibe, não pelo título</p>
      </header>

      <div className="tela">
        <Estante titulos={naEstante} aoEscolher={colocarNaCesta} />

        <div className="centro">
          <form className="caixa" onSubmit={buscar}>
            <h2 className="titulo-secao">QUAL A VIBE DE HOJE?</h2>
            <div className="campo">
              <input
                value={vibe}
                onChange={(e) => setVibe(e.target.value)}
                placeholder="ex: cozy witchy, spooky fun halloween..."
              />
              <button className="botao" type="submit">
                BUSCAR
              </button>
            </div>

            <div className="filtros">
              <div>
                <h3 className="titulo-secao">O QUE PROCURAR</h3>
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
                <h3 className="titulo-secao">SEM ESSES GÊNEROS</h3>
                <div className="grupo">
                  {GENEROS.map((g) => (
                    <button
                      type="button"
                      key={g}
                      className={
                        'etiqueta' + (excluidos.includes(g) ? ' excluida' : '')
                      }
                      onClick={() => alternarGenero(g)}
                    >
                      {g}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </form>

          <section>
            <h2 className="titulo-secao">SEM IDEIA? TENTA UMA DESSAS</h2>
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

      {reciboAberto && (
        <Recibo
          itens={cesta}
          vibe={vibe}
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
