import { useEffect, useRef } from 'react'
import { regulations } from '../data/f1Data'
import './Regulations.css'

function Regulations() {
  const sectionRef = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    )
    const elements = sectionRef.current?.querySelectorAll('.fade-in')
    elements?.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  return (
    <section id="regulations" className="section section-alt" ref={sectionRef}>
      <div className="container">
        <div className="section-header fade-in">
          <span className="section-tag">GAME CHANGERS</span>
          <h2 className="section-title">2026 Regulation <span className="accent">Revolution</span></h2>
          <p className="section-subtitle">The biggest rule change in a decade redefines what an F1 car looks like</p>
        </div>
        <div className="reg-grid">
          {regulations.map((reg, i) => (
            <div
              key={reg.tag}
              className="reg-card fade-in"
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <div className="reg-icon">{reg.icon}</div>
              <h3>{reg.title}</h3>
              <p>{reg.description}</p>
              <div className="reg-tag">{reg.tag}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Regulations
