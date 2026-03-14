import { useEffect, useRef, useState } from 'react'
import { getCircuitImage } from '../utils/assetMapper'
import { races as staticRaces } from '../data/f1Data'
import './RaceCalendar.css'

function RaceCalendar() {
  const sectionRef = useRef(null)
  const [races, setRaces] = useState([])
  const [nextRaceIndex, setNextRaceIndex] = useState(0)

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

  // Load race predictions (winner) from ml-predictions.json
  useEffect(() => {
    fetch('/ml-predictions.json')
      .then((res) => res.json())
      .then((data) => {
        const preds = data.racePredictions || []
        let foundNextRace = false;
        let nextIdx = 0;
        const now = new Date();

        const mergedRaces = preds.map((r, index) => {
          const staticRace = staticRaces.find((sr) => sr.round === r.round) || {};

          if (!foundNextRace && staticRace.date) {
            // Parses e.g., "Mar 13-15" to get the end day "15" and month "Mar"
            const parts = staticRace.date.split('-');
            let endDay = parts.length > 1 ? parts[1] : parts[0];
            // If the day contains the month (e.g. if the string doesn't follow the exact format), this is safer:
            endDay = endDay.replace(/[^0-9]/g, ''); 
            const monthStr = staticRace.date.split(' ')[0];

            const raceDate = new Date(`${monthStr} ${endDay}, 2026 23:59:59`);
            if (now <= raceDate) {
              nextIdx = index;
              foundNextRace = true;
            }
          }

          return {
            round: r.round,
            name: r.name,
            circuit: r.circuit,
            date: staticRace.date || '',
            flag: staticRace.flag || '',
            prediction: r.predictedWinner ? `🏆 ${r.predictedWinner}` : 'Prediction unavailable',
          };
        });

        setNextRaceIndex(nextIdx);
        setRaces(mergedRaces);
      })
      .catch((err) => {
        console.error('Failed to load race predictions', err)
      })
  }, [])

  return (
    <section id="calendar" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-tag">SEASON SCHEDULE</span>
          <h2 className="section-title">2026 Race <span className="accent">Calendar</span></h2>
          <p className="section-subtitle">24 races across 5 continents — the biggest F1 calendar ever</p>
        </div>
        <div className="calendar-grid">
          {races.map((race, i) => (
            <div
              key={race.round}
              className={`race-card ${i === nextRaceIndex ? 'next-race' : ''}`}
              style={{ transitionDelay: `${i * 50}ms` }}
            >
              <div className="race-round">ROUND {String(race.round).padStart(2, '0')}</div>
              <span className="race-flag">{race.flag}</span>
              <h3 className="race-name">{race.name}</h3>
              <p className="race-circuit">{race.circuit}</p>
              {race.date && <p className="race-date">📅 {race.date}</p>}
              <div className="race-prediction">{race.prediction}</div>
              <img 
                className="circuit-map" 
                src={getCircuitImage(race.circuit)} 
                alt={`${race.circuit} map`} 
                onError={(e) => { e.target.style.display = 'none'; }} 
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default RaceCalendar
