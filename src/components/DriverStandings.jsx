import { useEffect, useRef, useState } from 'react'
import { getDriverImage } from '../utils/assetMapper'
import './DriverStandings.css'

function DriverStandings() {
  const sectionRef = useRef(null)
  const [podiumDrivers, setPodiumDrivers] = useState([])
  const [restOfGrid, setRestOfGrid] = useState([])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    )

    const elements = sectionRef.current?.querySelectorAll('.fade-in')
    elements?.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  // Load ML predictions
  useEffect(() => {
    fetch('/ml-predictions.json')
      .then((res) => res.json())
      .then((data) => {
        const ds = data.driverStandings || {}
        setPodiumDrivers(ds.podium || [])
        setRestOfGrid(ds.rest || [])
      })
      .catch((err) => {
        console.error('Failed to load driver standings predictions', err)
      })
  }, [])

  const maxPoints = podiumDrivers.length ? podiumDrivers[0].points : 1

  return (
    <section id="drivers" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-tag">CHAMPIONSHIP FORECAST</span>
          <h2 className="section-title">Driver Standings <span className="accent">Prediction</span></h2>
          <p className="section-subtitle">Our predicted final standings for the 2026 World Drivers' Championship</p>
        </div>

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
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
                {driver.position === 1 && <div className="podium-crown">👑</div>}
                <div className="podium-position">P{driver.position}</div>
                <div className="driver-avatar" style={{ background: driver.gradient }}>
                  <span className="driver-number">{driver.number}</span>

                </div>
                <h3 className="driver-name">{driver.name}</h3>
                <span className={`team-name team-${driver.teamClass}`}>{driver.team}</span>
                <div className={`points-badge ${driver.position === 1 ? 'champion' : ''}`}>
                  {driver.points} PTS
                </div>
                <p className="driver-note">{driver.note}</p>
              </div>
            ))}
        </div>

        <div className="standings-table">
          {restOfGrid.map((driver, i) => (
            <div
              key={driver.number}
              className="standings-row"
              style={{ transitionDelay: `${i * 60}ms` }}
            >
              <span className="pos">{driver.pos}</span>
              <div className="driver-info">
                <img
                  className="row-driver-photo"
                  src={getDriverImage(driver.name)}
                  alt={driver.name}
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
                <span className="standing-number" style={{ color: driver.color }}>{driver.number}</span>
                <span className="standing-name">{driver.name}</span>
                <span className="standing-team">{driver.team}</span>
              </div>
              <span className="standing-points">{driver.points} PTS</span>
              <div className="points-bar" style={{ '--width': `${(driver.points / maxPoints) * 100}%` }}></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default DriverStandings
