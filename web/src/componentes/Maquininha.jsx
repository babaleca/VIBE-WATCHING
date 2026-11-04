// a maquininha de recibo. so desenho: recebe se esta imprimindo ou saindo da tela
function Maquininha({ fase }) {
  const classe = 'maquina' + (fase === 'imprimindo' ? ' imprimindo' : ' saindo')

  return (
    <div className={classe}>
      {/* a fenda por onde o papel sai */}
      <div className="fenda" />

      <div className="painel">
        <div className="visor">
          <span className="piscando">PRINTING...</span>
        </div>
        <div className="luzes">
          <i className="luz vermelha" />
          <i className="luz amarela" />
          <i className="luz verde" />
        </div>
      </div>

      <div className="marca">VIBE-PRINT 3000</div>
    </div>
  )
}

export default Maquininha
