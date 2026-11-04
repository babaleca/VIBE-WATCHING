// a caixinha de filme: cor sorteada pelo id + titulo escrito na capa
const CORES = ['#e4472f', '#f2b632', '#4fc1b0', '#8a6fd1', '#e87fa8', '#6fa8e8']

function CaixaFilme({ titulo, onClick, pequena }) {
  // o mesmo id sempre cai na mesma cor
  const cor = CORES[titulo.id % CORES.length]

  return (
    <button
      type="button"
      className={'caixa-filme' + (pequena ? ' pequena' : '')}
      style={{ '--cor': cor }}
      onClick={onClick}
      title={titulo.titulo}
    >
      <span className="faixa">{titulo.tipo === 'serie' ? 'SÉRIE' : 'FILME'}</span>
      <span className="nome">{titulo.titulo}</span>
    </button>
  )
}

export default CaixaFilme
