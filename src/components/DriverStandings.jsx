import { useEffect, useRef, useState } from 'react'
import { getDriverImage } from '../utils/assetMapper'
import './DriverStandings.css'

const TEAM_COLORS = {
  'McLaren':        'linear-gradient(135deg, #FF8000, #FF5500)',
  'Ferrari':        'linear-gradient(135deg, #E8002D, #AE0018)',
  'Red Bull Racing':'linear-gradient(135deg, #3671C6, #1B3A6B)',
  'Mercedes':       'linear-gradient(135deg, #27F4D2, #00A19C)',
  'Aston Martin':   'linear-gradient(135deg, #358C75, #1E5945)',
  'Alpine':         'linear-gradient(135deg, #0093CC, #FF87BC)',
  'Williams':       'linear-gradient(135deg, #64C4FF, #0057A8)',
  'Racing Bulls':   'linear-gradient(135deg, #6692FF, #3040A0)',
  'Haas':           'linear-gradient(135deg, #B6BABD, #E8002D)',
  'Audi':           'linear-gradient(135deg, #BB0000, #222222)',
  'Cadillac':       'linear-gradient(135deg, #00438D, #A1C7E5)',
}

const TEAM_COLORS_SOLID = {
  'McLaren':        '#FF8000',
  'Ferrari':        '#E8002D',
  'Red Bull Racing':'#3671C6',
  'Mercedes':       '#27F4D2',
  'Aston Martin':   '#358C75',
  'Alpine':         '#0093CC',
  'Williams':       '#64C4FF',
  'Racing Bulls':   '#6692FF',
  'Haas':           '#B6BABD',
  'Audi':           '#BB0000',
  'Cadillac':       '#00438D',
}

function DriverStandings() {
  const sectionRef = useRef(null)
  const [podiumDrivers, setPodiumDrivers] = useState([])
  const [restOfGrid, setRestOfGrid] = useState([])

  // ✅ FIX: re-run observer whenever restOfGrid changes so rows become visible
  useEffect(() => {
    if (!restOfGrid.length) return
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.05, rootMargin: '0px 0px -20px 0px' }
    )
    const elements = sectionRef.current?.querySelectorAll('.fade-in')
    elements?.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [restOfGrid]) // ← re-runs when rows are actually in the DOM

  useEffect(() => {
    fetch('/ml-predictions.json')
      .then((res) => res.json())
      .then((data) => {
        const drivers = data.season_standings?.drivers || []
        if (!drivers.length) return

        const mapped = drivers.map((d) => ({
          position:  d.position,
          number:    d.number,
          name:      d.name,
          team:      d.constructor,
          teamClass: d.constructor?.toLowerCase().replace(/\s+/g, '-') || 'ml',
          champPct:  d.championship_pct ?? 0,
          gradient:  TEAM_COLORS[d.constructor] || 'linear-gradient(135deg, #888, #444)',
          teamColor: TEAM_COLORS_SOLID[d.constructor] || '#ffffff',
        }))

        setPodiumDrivers(mapped.slice(0, 3))
        setRestOfGrid(mapped.slice(3))
      })
      .catch((err) => console.error('Failed to load driver standings', err))
  }, [])

  const maxPct = podiumDrivers[0]?.champPct || 1

  return (
    <section id="drivers" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-tag">CHAMPIONSHIP FORECAST</span>
          <h2 className="section-title">Driver Standings <span className="accent">Prediction</span></h2>
          <p className="section-subtitle">
            Predicted 2026 World Drivers' Championship — chance of winning the title
          </p>
        </div>

        {/* ── Top 3 podium cards ── */}
        <div className="podium-grid">
          {[podiumDrivers[1], podiumDrivers[0], podiumDrivers[2]]
            .filter(Boolean)
            .map((driver, i) => (
              <div
                key={driver.number}
                className={`podium-card podium-${driver.position}`}
                style={{ transitionDelay: `${i * 60}ms` }}
              >
                <img
                  className="driver-photo-layer"
                  src={getDriverImage(driver.name)}
                  alt={driver.name}
                  onError={(e) => { e.target.style.display = 'none' }}
                />
                {driver.position === 1 && <div className="podium-crown">👑</div>}
                <div className="podium-position">P{driver.position}</div>
                <div className="driver-avatar" style={{ background: driver.gradient }}>
                  <span className="driver-number">{driver.number}</span>
                </div>
                <h3 className="driver-name">{driver.name}</h3>
                <span className={`team-name team-${driver.teamClass}`}>{driver.team}</span>
                <div className={`points-badge ${driver.position === 1 ? 'champion' : ''}`}>
                  {driver.champPct}% TITLE CHANCE
                </div>
                <p className="driver-note">2026 ML Forecast</p>
              </div>
            ))}
        </div>

        {/* ── All remaining drivers P4–P22 ── */}
        <div className="standings-table">
          {restOfGrid.map((driver, i) => (
            <div
              key={driver.number}
              className="standings-row fade-in visible" // ✅ always visible, no observer dependency
              style={{ transitionDelay: `${i * 40}ms` }}
            >
              <span className="pos">{driver.position}</span>
              <div className="driver-info">
                <img
                  className="row-driver-photo"
                  src={getDriverImage(driver.name)}
                  alt={driver.name}
                  onError={(e) => { e.target.style.display = 'none' }}
                />
                <span className="standing-number" style={{ color: driver.teamColor }}>
                  {driver.number}
                </span>
                <span className="standing-name">{driver.name}</span>
                <span className="standing-team">{driver.team}</span>
              </div>
              <span className="standing-points">{driver.champPct}%</span>
              <div
                className="points-bar"
                style={{
                  '--width': `${(driver.champPct / maxPct) * 100}%`,
                  '--bar-color': driver.teamColor,
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default DriverStandings