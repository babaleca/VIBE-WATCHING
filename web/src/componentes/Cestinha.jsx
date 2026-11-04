import CaixaFilme from './CaixaFilme'

// a cestinha: guarda o que a pessoa escolheu. clicar numa caixa devolve pra estante
function Cestinha({ itens, aoDevolver, aoFinalizar }) {
  return (
    <aside className="cestinha">
      <h2 className="placa">CESTINHA</h2>

      <div className="cesta">
        <div className="itens-cesta">
          {itens.map((t) => (
            <CaixaFilme
              key={t.id + t.tipo}
              titulo={t}
              pequena
              onClick={() => aoDevolver(t)}
            />
          ))}
          {itens.length === 0 && (
            <p className="vazio">vazia por enquanto. clica numa caixa da estante!</p>
          )}
        </div>

        {/* a frente da cesta fica por cima e esconde a parte de baixo das caixas */}
        <div className="frente-cesta">
          <div className="aro" />
          <div className="corpo-cesta">
            <span className="etiqueta-cesta">
              {itens.length} {itens.length === 1 ? 'ITEM' : 'ITENS'}
            </span>
          </div>
        </div>
      </div>

      <button
        type="button"
        className="botao"
        disabled={itens.length === 0}
        onClick={aoFinalizar}
      >
        FINALIZAR
      </button>
    </aside>
  )
}

export default Cestinha
