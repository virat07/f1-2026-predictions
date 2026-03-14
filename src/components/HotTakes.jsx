import { useEffect, useRef } from 'react'
import { hotTakes } from '../data/f1Data'
import './HotTakes.css'

function HotTakes() {
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
    <section id="hot-takes" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-header fade-in">
          <span className="section-tag">🔥 SPICY OPINIONS</span>
          <h2 className="section-title">Our Bold <span className="accent">Hot Takes</span></h2>
          <p className="section-subtitle">Controversial predictions that will either age like fine wine or absolute milk</p>
        </div>
        <div className="takes-grid">
          {hotTakes.map((take, i) => (
            <div
              key={i}
              className="take-card fade-in"
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <div className="take-heat">
                <span>{take.peppers}</span>
                <span className="heat-label">{take.label}</span>
              </div>
              <h3>{take.title}</h3>
              <p>{take.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HotTakes
