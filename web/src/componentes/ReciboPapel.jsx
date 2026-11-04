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

function ReciboPapel({ itens, numero, data, ref }) {
  const filmes = itens.filter((t) => t.tipo === 'filme').length
  const series = itens.length - filmes

  // agrupa os itens por vibe (na ordem em que apareceram)
  const grupos = []
  for (const item of itens) {
    let grupo = grupos.find((g) => g.vibe === item.vibe)
    if (!grupo) {
      grupo = { vibe: item.vibe, itens: [] }
      grupos.push(grupo)
    }
    grupo.itens.push(item)
  }

  return (
    // o "wrap" tem uma margem em volta: no JPEG ela vira a moldura azul
    <div className="recibo-wrap" ref={ref}>
      <div className="recibo">
        <div className="recibo-topo">
          <div className="recibo-logo">VIBE WATCHING</div>
          <div>VIDEO RENTAL</div>
          <div className="recibo-pequeno">rental receipt</div>
        </div>

        <div className="pontilhada" />

        <div className="recibo-info">
          <span>No. {numero}</span>
          <span>{data.toLocaleString('en-US', FORMATO)}</span>
        </div>

        <div className="pontilhada" />

        {grupos.map((g) => (
          <div key={g.vibe}>
            {g.vibe && <div className="recibo-vibe">VIBE: "{g.vibe}"</div>}
            <ul className="recibo-lista">
              {g.itens.map((t) => (
                <li key={t.id + t.tipo}>
                  <span className="item-nome">{t.titulo}</span>
                  <span className="item-tipo">{t.tipo === 'serie' ? 'SERIES' : 'MOVIE'}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}

        <div className="pontilhada" />

        <div className="recibo-total">
          <span>TOTAL ITEMS</span>
          <span>{itens.length}</span>
        </div>
        <div className="recibo-pequeno">
          {filmes} {filmes === 1 ? 'movie' : 'movies'} · {series} series
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
          THANKS FOR VISITING!
          <br />
          PLEASE BE KIND, REWIND
        </div>
      </div>
    </div>
  )
}

export default ReciboPapel
