import { useState } from 'react'
import { CAPA } from '../api'

// a caixinha de filme: mostra a capa; sem capa, vira uma caixa colorida com o titulo
const CORES = ['#e4472f', '#f2b632', '#4fc1b0', '#8a6fd1', '#e87fa8', '#6fa8e8']

function CaixaFilme({ titulo, onClick, pequena }) {
  // se a imagem falhar ao carregar, volta pra caixa colorida
  const [capaFalhou, setCapaFalhou] = useState(false)
  const temCapa = titulo.poster && !capaFalhou

  // o mesmo id sempre cai na mesma cor
  const cor = CORES[titulo.id % CORES.length]

  // dica ao parar o mouse: titulo, ano e o motivo do reranker (se tiver)
  const dica = [
    titulo.ano ? `${titulo.titulo} (${titulo.ano})` : titulo.titulo,
    titulo.motivo,
  ]
    .filter(Boolean)
    .join(' - ')

  return (
    <button
      type="button"
      className={
        'caixa-filme' + (pequena ? ' pequena' : '') + (temCapa ? ' com-capa' : '')
      }
      style={{ '--cor': cor }}
      onClick={onClick}
      title={dica}
    >
      <span className="faixa">{titulo.tipo === 'serie' ? 'SERIES' : 'MOVIE'}</span>

      {temCapa ? (
        <>
          <img
            className="capa"
            src={`${CAPA}${titulo.poster}`}
            alt={titulo.titulo}
            loading="lazy"
            onError={() => setCapaFalhou(true)}
          />
          <span className="legenda">{titulo.titulo}</span>
        </>
      ) : (
        <span className="nome">{titulo.titulo}</span>
      )}
    </button>
  )
}

export default CaixaFilme
