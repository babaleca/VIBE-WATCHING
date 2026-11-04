import { useEffect, useRef, useState } from 'react'
import { toJpeg } from 'html-to-image'
import * as sons from '../sons'
import Maquininha from './Maquininha'
import ReciboPapel from './ReciboPapel'
import './Recibo.css'

// a tela do recibo: escurece o fundo, imprime e depois deixa baixar
function Recibo({ itens, vibe, aoFechar }) {
  // 'imprimindo' -> 'pronto'
  const [fase, setFase] = useState('imprimindo')
  const [baixando, setBaixando] = useState(false)
  const papelRef = useRef(null)

  // numero e data sao sorteados UMA vez, senao mudariam a cada atualizacao da tela
  const [numero] = useState(() => String(Date.now()).slice(-6))
  const [data] = useState(() => new Date())

  // quanto mais itens, mais tempo imprimindo, mas com teto de 3 segundos
  const segundos = Math.min(1.3 + itens.length * 0.08, 3)
  const passos = Math.round(segundos * 10) // 10 "quadros" por segundo: movimento de pixel art

  // tiques de impressora enquanto o papel sobe; para sozinho quando a fase muda
  useEffect(() => {
    if (fase !== 'imprimindo') return
    return sons.imprimir(segundos, passos)
  }, [fase, segundos, passos])

  // tecla Esc fecha
  useEffect(() => {
    function teclou(e) {
      if (e.key === 'Escape') aoFechar()
    }
    window.addEventListener('keydown', teclou)
    return () => window.removeEventListener('keydown', teclou)
  }, [aoFechar])

  // clicar no fundo (fora do recibo) fecha
  function cliqueNoFundo(e) {
    if (e.target === e.currentTarget) aoFechar()
  }

  async function baixar() {
    sons.baixar()
    setBaixando(true)
    try {
      const url = await toJpeg(papelRef.current, {
        quality: 0.95,
        pixelRatio: 3,
        backgroundColor: '#1b1f3b',
      })
      const link = document.createElement('a')
      link.href = url
      link.download = 'recibo-vibe-watching.jpg'
      link.click()
    } catch (erro) {
      console.error('nao consegui gerar a imagem', erro)
    }
    setBaixando(false)
  }

  return (
    <div className="recibo-fundo" onClick={cliqueNoFundo}>
      <button className="fechar" onClick={aoFechar} aria-label="Fechar">
        X
      </button>

      <div className="palco">
        {/* o papel sobe pela fenda; quando a animacao termina, a fase vira 'pronto' */}
        <div className="saida">
          <div
            className="folha"
            style={{ '--tempo': `${segundos}s`, '--passos': passos }}
            onAnimationEnd={() => {
              setFase('pronto')
              sons.pronto()
            }}
          >
            <ReciboPapel
              ref={papelRef}
              itens={itens}
              vibe={vibe}
              numero={numero}
              data={data}
            />
          </div>
        </div>

        <Maquininha fase={fase} />

        {fase === 'pronto' && (
          <div className="acoes">
            <button className="botao" onClick={baixar} disabled={baixando}>
              {baixando ? 'GERANDO...' : 'BAIXAR JPEG'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Recibo
