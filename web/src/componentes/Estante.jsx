import CaixaFilme from './CaixaFilme'

// a estante: lista com rolagem propria, so ela rola (a pagina nao)
function Estante({ titulos, aoEscolher, carregando, buscou }) {
  // junta de 3 em 3: cada grupo fica apoiado em uma tabua
  const niveis = []
  for (let i = 0; i < titulos.length; i += 3) {
    niveis.push(titulos.slice(i, i + 3))
  }

  return (
    <aside className="estante">
      <h2 className="placa">SHELF ({titulos.length})</h2>
      <div className="prateleiras">
        {carregando ? (
          <p className="vazio piscando">DIGGING THROUGH THE SHELVES...</p>
        ) : (
          niveis.map((grupo) => (
            <div className="nivel" key={grupo[0].id + grupo[0].tipo}>
              <div className="caixas">
                {grupo.map((t) => (
                  <CaixaFilme
                    key={t.id + t.tipo}
                    titulo={t}
                    onClick={(e) => aoEscolher(t, e.currentTarget)}
                  />
                ))}
              </div>
              <div className="tabua" />
            </div>
          ))
        )}

        {!carregando && titulos.length === 0 && (
          <p className="vazio">
            {buscou
              ? "The shelf is empty: nothing else found, or you took it all!"
              : 'Type a vibe and hit SEARCH to stock the shelf.'}
          </p>
        )}
      </div>
    </aside>
  )
}

export default Estante
