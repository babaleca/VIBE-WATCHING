// o papel do recibo. e isso que vira o JPEG
const FORMATO = { dateStyle: 'short', timeStyle: 'short' }

// gera barras "aleatorias" mas sempre iguais pro mesmo numero (tipo codigo de barras)
function barrasDoNumero(numero) {
  let semente = Number(numero) || 1
  const barras = []
  for (let i = 0; i < 36; i++) {
    semente = (semente * 9301 + 49297) % 233280
    barras.push(1 + Math.floor((semente / 233280) * 4)) // largura de 1 a 4
  }
  return barras
}

function ReciboPapel({ itens, vibe, numero, data, ref }) {
  const filmes = itens.filter((t) => t.tipo === 'filme').length
  const series = itens.length - filmes

  return (
    // o "wrap" tem uma margem em volta: no JPEG ela vira a moldura azul
    <div className="recibo-wrap" ref={ref}>
      <div className="recibo">
        <div className="recibo-topo">
          <div className="recibo-logo">VIBE WATCHING</div>
          <div>VÍDEO LOCADORA</div>
          <div className="recibo-pequeno">recibo de locação</div>
        </div>

        <div className="pontilhada" />

        <div className="recibo-info">
          <span>Nº {numero}</span>
          <span>{data.toLocaleString('pt-BR', FORMATO)}</span>
        </div>
        {vibe && <div className="recibo-vibe">VIBE: "{vibe}"</div>}

        <div className="pontilhada" />

        <ul className="recibo-lista">
          {itens.map((t) => (
            <li key={t.id + t.tipo}>
              <span className="item-nome">{t.titulo}</span>
              <span className="item-tipo">{t.tipo === 'serie' ? 'SÉRIE' : 'FILME'}</span>
            </li>
          ))}
        </ul>

        <div className="pontilhada" />

        <div className="recibo-total">
          <span>TOTAL DE ITENS</span>
          <span>{itens.length}</span>
        </div>
        <div className="recibo-pequeno">
          {filmes} {filmes === 1 ? 'filme' : 'filmes'} · {series}{' '}
          {series === 1 ? 'série' : 'séries'}
        </div>

        <div className="pontilhada" />

        <div className="codigo">
          {barrasDoNumero(numero).map((largura, i) => (
            <i
              key={i}
              style={{
                width: largura * 2,
                background: i % 2 === 0 ? 'var(--tinta)' : 'transparent',
              }}
            />
          ))}
        </div>

        <div className="recibo-rodape">
          OBRIGADA PELA VISITA!
          <br />
          REBOBINE ANTES DE DEVOLVER
        </div>
      </div>
    </div>
  )
}

export default ReciboPapel
