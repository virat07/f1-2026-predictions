import { useEffect, useRef } from 'react'
import './Hero.css'

function Hero() {
  const particlesRef = useRef(null)
  const statsRef = useRef(null)

  useEffect(() => {
    // Create particles
    const container = particlesRef.current
    if (!container) return

    for (let i = 0; i < 30; i++) {
      const particle = document.createElement('div')
      particle.className = 'hero-particle'
      const x = Math.random() * 100
      const duration = 8 + Math.random() * 12
      const delay = Math.random() * duration
      const size = 1 + Math.random() * 3
      const opacity = 0.2 + Math.random() * 0.5

      particle.style.cssText = `
        left: ${x}%;
        width: ${size}px;
        height: ${size}px;
        animation-duration: ${duration}s;
        animation-delay: -${delay}s;
        opacity: ${opacity};
        background: ${Math.random() > 0.5 ? 'rgba(232, 0, 45, 0.6)' : 'rgba(255, 107, 53, 0.4)'};
      `
      container.appendChild(particle)
    }

    return () => {
      while (container.firstChild) {
        container.removeChild(container.firstChild)
      }
    }
  }, [])

  // Counter animation
  useEffect(() => {
    const stats = statsRef.current
    if (!stats) return

    const values = stats.querySelectorAll('.hero-stat-value')
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target
            const finalVal = parseInt(el.dataset.value)
            animateCounter(el, 0, finalVal, 1500)
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.5 }
    )

    values.forEach((v) => observer.observe(v))
    return () => observer.disconnect()
  }, [])

  const animateCounter = (el, start, end, duration) => {
    const startTime = performance.now()
    const update = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      el.textContent = Math.round(start + (end - start) * eased)
      if (progress < 1) requestAnimationFrame(update)
    }
    requestAnimationFrame(update)
  }

  const handleExplore = (e) => {
    e.preventDefault()
    const el = document.getElementById('drivers')
    if (el) {
      const top = el.getBoundingClientRect().top + window.pageYOffset - 70
      window.scrollTo({ top, behavior: 'smooth' })
    }
  }

  const stats = [
    { value: 24, label: 'Races' },
    { value: 11, label: 'Teams' },
    { value: 22, label: 'Drivers' },
    { value: 1, label: 'Champion' },
  ]

  return (
    <section id="hero" className="hero-section">
      <div className="hero-bg"></div>
      <div className="hero-overlay"></div>
      <div className="hero-particles" ref={particlesRef}></div>
      <div className="hero-content">
        <div className="hero-badge">NEW ERA OF RACING</div>
        <h1 className="hero-title">
          <span className="hero-title-line">FORMULA 1</span>
          <span className="hero-title-year">2026</span>
          <span className="hero-title-sub">PREDICTIONS</span>
        </h1>
        <p className="hero-description">
          Active aero. New power units. A revolutionary era begins. Here are our bold predictions for the most anticipated season in F1 history.
        </p>
        <div className="hero-stats" ref={statsRef}>
          {stats.map((stat) => (
            <div key={stat.label} className="hero-stat">
              <span className="hero-stat-value" data-value={stat.value}>0</span>
              <span className="hero-stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
        <a href="#drivers" className="hero-cta" onClick={handleExplore}>
          Explore Predictions <span className="cta-arrow">→</span>
        </a>
      </div>
      <div className="scroll-indicator">
        <div className="scroll-mouse">
          <div className="scroll-wheel"></div>
        </div>
        <span>Scroll to explore</span>
      </div>
    </section>
  )
}

export default Hero
