import { useEffect, useRef, useState } from 'react'
import './ConstructorStandings.css'

function ConstructorStandings() {
  const sectionRef = useRef(null)
  const [constructors, setConstructors] = useState([])

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
        setConstructors(data.constructorStandings || [])
      })
      .catch((err) => {
        console.error('Failed to load constructor standings predictions', err)
      })
  }, [])

  const maxPoints = constructors.length ? constructors[0].points : 1

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
              className="constructor-card"
              style={{ transitionDelay: `${i * 80}ms` }}
            >
              <div className="constructor-rank">{team.rank}</div>
              <div className="constructor-color" style={{ background: team.color }}></div>
              <div className="constructor-info">
                <h3>{team.name}</h3>
                <p className="constructor-drivers">{team.drivers}</p>
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
    </section>
  )
}

export default ConstructorStandings
