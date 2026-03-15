import { useEffect, useMemo, useRef, useState } from 'react'
import { getDriverImage, getTeamCarImage, getTeamImage } from '../utils/assetMapper'
import './ConstructorStandings.css'

// Official 2026 team colors
const TEAM_COLORS = {
  'Ferrari':        '#E8002D',
  'Red Bull Racing':'#3671C6',
  'Mercedes':       '#27F4D2',
  'McLaren':        '#FF8000',
  'Aston Martin':   '#358C75',
  'Alpine':         '#0093CC',
  'Williams':       '#64C4FF',
  'Racing Bulls':   '#6692FF',
  'Haas':           '#B6BABD',
  'Audi':           '#BB0000',
  'Cadillac':       '#00438D',
}

const teamDrivers = {
  'ferrari':        ['Lewis Hamilton', 'Charles Leclerc'],
  'red bull racing':['Max Verstappen', 'Isack Hadjar'],
  'mercedes':       ['George Russell', 'Andrea Kimi Antonelli'],
  'mclaren':        ['Lando Norris', 'Oscar Piastri'],
  'aston martin':   ['Fernando Alonso', 'Lance Stroll'],
  'alpine':         ['Pierre Gasly', 'Franco Colapinto'],
  'williams':       ['Alexander Albon', 'Carlos Sainz'],
  'racing bulls':   ['Liam Lawson', 'Arvid Lindblad'],
  'haas':           ['Esteban Ocon', 'Oliver Bearman'],
  'audi':           ['Nico Hülkenberg', 'Gabriel Bortoleto'],
  'cadillac':       ['Sergio Pérez', 'Valtteri Bottas'],
}

const normalizeTeamName = (name) => {
  if (!name) return ''
  return name.toLowerCase().trim()
}

function ConstructorStandings() {
  const sectionRef = useRef(null)
  const [constructors, setConstructors] = useState([])
  const [racePredictions, setRacePredictions] = useState([])
  const [selectedTeam, setSelectedTeam] = useState(null)

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

  // Load ML predictions
  useEffect(() => {
    fetch('/ml-predictions.json')
      .then((res) => res.json())
      .then((data) => {
        // ✅ FIX: new JSON uses season_standings.constructors (snake_case)
        const rawConstructors = data.season_standings?.constructors || []
        // ✅ FIX: new JSON uses race_predictions (snake_case)
        const rawRacePreds = data.race_predictions || []

        // ✅ FIX: map new flat objects → shape the component expects
        const mapped = rawConstructors.map((c) => ({
          rank:   c.rank,
          name:   c.constructor,
          points: Math.round(c.predicted_points),
          color:  TEAM_COLORS[c.constructor] || '#ffffff',
          note:   'ML Grid Forecast',
          drivers: (teamDrivers[normalizeTeamName(c.constructor)] || []).join(' · '),
        }))

        setConstructors(mapped)
        setRacePredictions(rawRacePreds)
      })
      .catch((err) => {
        console.error('Failed to load constructor standings predictions', err)
      })
  }, [])

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setSelectedTeam(null)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const maxPoints = constructors.length ? constructors[0].points : 1

  // ✅ FIX: count wins using predicted_winner (snake_case)
  const winsByTeam = useMemo(() => {
    return racePredictions.reduce((acc, race) => {
      const teamKey = normalizeTeamName(race.predicted_winner)
      if (!teamKey) return acc
      acc[teamKey] = (acc[teamKey] || 0) + 1
      return acc
    }, {})
  }, [racePredictions])

  const selectedTeamKey = normalizeTeamName(selectedTeam?.name)
  const selectedTeamDrivers = selectedTeamKey ? (teamDrivers[selectedTeamKey] || []) : []
  const selectedTeamWins = selectedTeamKey ? (winsByTeam[selectedTeamKey] || 0) : 0
  const selectedTeamCar = selectedTeamKey ? getTeamCarImage(selectedTeamKey) : ''

  return (
    <section id="constructors" className="section section-alt" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-tag">TEAM BATTLE</span>
          <h2 className="section-title">Constructor Standings <span className="accent">Prediction</span></h2>
          <p className="section-subtitle">Who will dominate in the new regulation era?</p>
        </div>
        <div className="constructor-grid">
          {constructors.map((team, i) => (
            <div
              key={team.rank}
              className={`constructor-card ${selectedTeam?.name === team.name ? 'is-selected' : ''}`}
              style={{ transitionDelay: `${i * 80}ms` }}
              onClick={() => setSelectedTeam(team)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') setSelectedTeam(team)
              }}
            >
              <div className="constructor-rank">{team.rank}</div>
              <div className="constructor-color" style={{ background: team.color }}></div>
              <img
                className="team-car-img"
                src={getTeamImage(team.name)}
                alt={team.name}
                onError={(e) => { e.target.style.display = 'none' }}
              />
              <div className="constructor-info">
                <h3>
                  <button
                    type="button"
                    className="team-name-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedTeam(team)
                    }}
                  >
                    {team.name}
                  </button>
                </h3>
                <p className="constructor-drivers">
                  {(teamDrivers[normalizeTeamName(team.name)] || []).join(' · ') || 'Drivers TBD'}
                </p>
                <p className="constructor-points">{team.points} PTS</p>
                <p className="constructor-note">{team.note}</p>
              </div>
              <div
                className="constructor-bar"
                style={{
                  '--bar-width': `${(team.points / maxPoints) * 100}%`,
                  '--bar-color': team.color,
                }}
              ></div>
            </div>
          ))}
        </div>
      </div>

      {selectedTeam && (
        <div
          className="constructor-modal-backdrop"
          role="presentation"
          onClick={() => setSelectedTeam(null)}
        >
          <div
            className="constructor-modal"
            role="dialog"
            aria-modal="true"
            aria-label={`${selectedTeam.name} details`}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="constructor-modal-close"
              type="button"
              onClick={() => setSelectedTeam(null)}
            >
              ×
            </button>
            <div className="constructor-detail-header">
              <p className="constructor-detail-label">Selected Team</p>
              <h3 className="constructor-detail-title">{selectedTeam.name}</h3>
              <p className="constructor-detail-wins">
                {selectedTeamWins} predicted win{selectedTeamWins !== 1 ? 's' : ''} in 2026
              </p>
            </div>
            <div className="constructor-detail-car-wrap">
              <img
                className="constructor-detail-car"
                src={selectedTeamCar}
                alt={`${selectedTeam.name} 2026 car`}
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
            <div className="constructor-detail-drivers">
              {selectedTeamDrivers.map((driver) => (
                <div key={driver} className="constructor-driver">
                  <img
                    className="constructor-driver-img"
                    src={getDriverImage(driver)}
                    alt={driver}
                    onError={(e) => { e.target.style.display = 'none' }}
                  />
                  <span>{driver}</span>
                </div>
              ))}
              {selectedTeamDrivers.length === 0 && (
                <div className="constructor-driver empty">Drivers TBD</div>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default ConstructorStandings