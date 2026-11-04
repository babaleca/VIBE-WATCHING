import CaixaFilme from './CaixaFilme'

// a estante: lista com rolagem propria, so ela rola (a pagina nao)
function Estante({ titulos, aoEscolher }) {
  // junta de 3 em 3: cada grupo fica apoiado em uma tabua
  const niveis = []
  for (let i = 0; i < titulos.length; i += 3) {
    niveis.push(titulos.slice(i, i + 3))
  }

  return (
    <aside className="estante">
      <h2 className="placa">ESTANTE ({titulos.length})</h2>
      <div className="prateleiras">
        {niveis.map((grupo) => (
          <div className="nivel" key={grupo[0].id + grupo[0].tipo}>
            <div className="caixas">
              {grupo.map((t) => (
                <CaixaFilme
                  key={t.id + t.tipo}
                  titulo={t}
                  onClick={() => aoEscolher(t)}
                />
              ))}
            </div>
            <div className="tabua" />
          </div>
        ))}
        {titulos.length === 0 && (
          <p className="vazio">a estante esvaziou, você levou tudo!</p>
        )}
      </div>
    </aside>
  )
}

export default Estante
