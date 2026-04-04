import { useState, useEffect, useRef } from 'react'
import { races } from '../data/f1Data'
import { getCircuitImage } from '../utils/assetMapper'
import './Hero.css'

function Hero() {
  const particlesRef = useRef(null)
  const statsRef = useRef(null)
  const [nextRace, setNextRace] = useState(null)
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })
  const [activeModal, setActiveModal] = useState(null) // 'circuit' or 'winner'
  const [selectedWinner, setSelectedWinner] = useState(null)
  const [scrollVisible, setScrollVisible] = useState(true)

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setScrollVisible(false)
      } else {
        setScrollVisible(true)
      }
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

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

  // Countdown Logic
  useEffect(() => {
    // Find next race
    const now = new Date()
    const upcoming = races.find(race => {
      const parts = race.date.split(/[–-]/)
      const endDay = parts.length > 1 ? parts[1].trim().replace(/[^0-9]/g, '') : parts[0].replace(/[^0-9]/g, '')
      const monthStr = race.date.split(' ')[0]
      const raceDate = new Date(`${monthStr} ${endDay}, 2026 23:59:59`)
      return raceDate >= now
    })

    if (upcoming) {
      setNextRace(upcoming)

      const parts = upcoming.date.split(/[–-]/)
      const startDay = parts[0].trim().replace(/[^0-9]/g, '')
      const monthStr = upcoming.date.split(' ')[0]
      const targetDate = new Date(`${monthStr} ${startDay}, 2026 09:00:00`).getTime()

      const timer = setInterval(() => {
        const currentTime = new Date().getTime()
        const difference = targetDate - currentTime

        if (difference > 0) {
          setTimeLeft({
            days: Math.floor(difference / (1000 * 60 * 60 * 24)),
            hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
            minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
            seconds: Math.floor((difference % (1000 * 60)) / 1000)
          })
        } else {
          clearInterval(timer)
        }
      }, 1000)

      return () => clearInterval(timer)
    }
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

  // Helper to get YouTube ID for common winners/tracks
  const getWinnerVideoId = (winner, track = "") => {
    const driver = winner.split(' ')[0];
    const trackLower = track.toLowerCase();
    
    // Real-world F1 YouTube Highlight Mapping (Embeddable IDs)
    const trackHighlights = {
      'sakhir': {
        'Verstappen': 'K0SjW8W6Xf8', // 2024 Bahrain
        'Leclerc': 'nZq5g6Gf6I0'     // 2022 Bahrain
      },
      'melbourne': {
        'Sainz': 'zS4T27R-QYo',      // 2024 Australia
        'Verstappen': '8_m7Y9U9-Zk'  // 2023 Australia
      },
      'monaco': {
        'Leclerc': 'fN6Gv-9pUoM',    // 2024 Monaco (Cinematic)
        'Perez': 'vIIDvKqA7uM'       // 2022 Monaco
      }
    };

    const driverHighlights = {
      'Verstappen': 'A0hnd75k9S8',
      'Hamilton': 'jWNSv9hI_kM',
      'Leclerc': 'nZq5g6Gf6I0',
      'Norris': 'vIIDvKqA7uM',
      'Sainz': 'zS4T27R-QYo',
      'Perez': '8_m7Y9U9-Zk'
    };

    // Find if track matches any key in our mapping
    const trackKey = Object.keys(trackHighlights).find(k => trackLower.includes(k));
    if (trackKey && trackHighlights[trackKey][driver]) {
      return trackHighlights[trackKey][driver];
    }

    return driverHighlights[driver] || 'v4Z9Ie_S_D0';
  }

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

        {nextRace && (
          <div className="next-race-container">
            <div className="countdown-grid">
              <div className="countdown-item">
                <span className="countdown-val">{timeLeft.days}</span>
                <span className="countdown-label">DAYS</span>
              </div>
              <div className="countdown-item">
                <span className="countdown-val">{timeLeft.hours}</span>
                <span className="countdown-label">HRS</span>
              </div>
              <div className="countdown-item">
                <span className="countdown-val">{timeLeft.minutes}</span>
                <span className="countdown-label">MIN</span>
              </div>
              <div className="countdown-item">
                <span className="countdown-val">{timeLeft.seconds}</span>
                <span className="countdown-label">SEC</span>
              </div>
            </div>
            <div className="next-race-info">
              <span className="next-tag">NEXT ROUND</span>
              <h3 className="next-name clickable" onClick={() => setActiveModal('circuit')}>
                {nextRace.flag} {nextRace.name}
              </h3>
              <p className="next-circuit clickable" onClick={() => setActiveModal('circuit')}>
                {nextRace.circuit} • {nextRace.date}
              </p>

              {nextRace.previousWinners && (
                <div className="prev-winners">
                  <span className="prev-title">PAST WINNERS:</span>
                  <div className="prev-list">
                    {nextRace.previousWinners.map(winner => (
                      <span
                        key={winner}
                        className="prev-winner clickable-badge"
                        onClick={() => { setSelectedWinner(winner); setActiveModal('winner'); }}
                      >
                        {winner}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Interactive Modals ── */}
        {activeModal === 'circuit' && nextRace && (
          <div className="hero-modal-overlay" onClick={() => setActiveModal(null)}>
            <div className="hero-modal-content" onClick={e => e.stopPropagation()}>
              <button className="close-hero-modal" onClick={() => setActiveModal(null)}>×</button>
              <div className="hero-modal-header">
                <span className="modal-badge">CIRCUIT MAP</span>
                <h2>{nextRace.name}</h2>
                <p>{nextRace.circuit}</p>
              </div>
              <div className="hero-modal-body">
                <img src={getCircuitImage(nextRace.circuit)} alt={nextRace.circuit} className="modal-circuit-img" />
              </div>
            </div>
          </div>
        )}

        {activeModal === 'winner' && selectedWinner && (
          <div className="hero-modal-overlay" onClick={() => setActiveModal(null)}>
            <div className="hero-modal-content winner-moment" onClick={e => e.stopPropagation()}>
              <button className="close-hero-modal" onClick={() => setActiveModal(null)}>×</button>
              <div className="hero-modal-header">
                <span className="modal-badge">WINNER MOMENT</span>
                <h2>{selectedWinner}</h2>
                <p>Podium Highlight • Official F1 Archives</p>
              </div>
              <div className="hero-modal-body video-container">
                <div className="video-player-wrapper">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${getWinnerVideoId(selectedWinner, nextRace.name)}?origin=http://localhost:5173&autoplay=1&rel=0`}
                    title="YouTube video player"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                  ></iframe>
                </div>
              </div>
            </div>
          </div>
        )}
        <a href="#drivers" className="hero-cta" onClick={handleExplore}>
          Explore Predictions <span className="cta-arrow">→</span>
        </a>
      </div>

      <div className={`scroll-indicator ${!scrollVisible ? 'hidden' : ''}`}>
        <div className="scroll-mouse">
          <div className="scroll-wheel"></div>
        </div>
        <span>Scroll to explore</span>
      </div>
    </section>
  )
}

export default Hero
