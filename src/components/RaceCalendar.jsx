import { useEffect, useRef, useState } from 'react'
import { getCircuitImage } from '../utils/assetMapper'
import { races as staticRaces, allDrivers, allTeams } from '../data/f1Data'
import { supabase } from '../utils/supabaseClient'
import './RaceCalendar.css'

function RaceCalendar({ notify }) {
  const sectionRef = useRef(null)
  const [races, setRaces] = useState([])
  const [actualResults, setActualResults] = useState({})
  const [nextRaceIndex, setNextRaceIndex] = useState(0)
  const [selectedCircuit, setSelectedCircuit] = useState(null)
  const [userPredictions, setUserPredictions] = useState(() => {
    const saved = localStorage.getItem('f1_user_predictions_v2')
    return saved ? JSON.parse(saved) : {}
  })
  const [username, setUsername] = useState(localStorage.getItem('f1_username') || '')

  const handleUserPredict = (round, type, driverName) => {
    const roundPreds = userPredictions[round] || {}
    const newRoundPreds = { ...roundPreds, [type]: driverName }
    const newPredictions = { ...userPredictions, [round]: newRoundPreds }
    setUserPredictions(newPredictions)
    localStorage.setItem('f1_user_predictions_v2', JSON.stringify(newPredictions))
    if (username) syncPredictionToSupabase(round, newRoundPreds)
  }

  const syncPredictionToSupabase = async (round, predictions) => {
    try {
      const { error: userError } = await supabase
        .from('leaderboard')
        .upsert({ username, joined_at: new Date().toISOString() }, { onConflict: 'username' })
      if (userError) throw userError
      const { error: predError } = await supabase
        .from('predictions')
        .upsert({ username, round, predictions, created_at: new Date().toISOString() }, { onConflict: 'username,round' })
      if (predError) throw predError
      notify('Prediction saved!', 'success')
    } catch (error) {
      notify(`Sync Failed: ${error.message}`, 'error')
    }
  }

  const handleUsernameChange = (val) => {
    setUsername(val)
    localStorage.setItem('f1_username', val)
  }

  useEffect(() => {
    const fetchResults = async () => {
      const { data } = await supabase.from('actual_results').select('*')
      if (data) {
        const map = data.reduce((acc, curr) => { acc[curr.round] = curr; return acc }, {})
        setActualResults(map)
      }
    }
    fetchResults()
    const channel = supabase
      .channel('results_realtime')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'actual_results' }, (payload) => {
        setActualResults(prev => ({ ...prev, [payload.new.round]: payload.new }))
      })
      .subscribe()
    return () => supabase.removeChannel(channel)
  }, [])

  useEffect(() => {
    fetch('/ml-predictions.json')
      .then(res => res.json())
      .then(data => {
        const preds = data.race_predictions || []
        let foundNextRace = false
        let nextIdx = 0
        const now = new Date()
        const mergedRaces = preds.map((r, index) => {
          const staticRace = staticRaces.find(sr => sr.round === r.round) || {}
          if (!foundNextRace && staticRace.date) {
            const parts = staticRace.date.split(/[–-]/)
            let endDay = parts.length > 1 ? parts[1].trim() : parts[0]
            endDay = endDay.replace(/[^0-9]/g, '')
            const monthStr = staticRace.date.split(' ')[0]
            const raceDate = new Date(`${monthStr} ${endDay}, 2026 23:59:59`)
            if (now <= raceDate) { nextIdx = index; foundNextRace = true }
          }
          const winner = r.predicted_winner || null
          const podium = r.predicted_podium
          const topProbs = (r.win_probabilities || []).slice(0, 3)
          return {
            round: r.round,
            name: staticRace.name || r.name,
            circuit: staticRace.circuit || r.circuit,
            date: staticRace.date || r.date || '',
            flag: staticRace.flag || '',
            prediction: winner,
            podium,
            topProbs,
            isSprint: staticRace.isSprint || r.sprint || false,
          }
        })
        setNextRaceIndex(nextIdx)
        setRaces(mergedRaces)
      })
      .catch(err => console.error('Failed to load race predictions', err))
  }, [])

  return (
    <section id="calendar" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-tag">SEASON SCHEDULE</span>
          <h2 className="section-title">2026 Race <span className="accent">Calendar</span></h2>
          <p className="section-subtitle">24 races across 5 continents — the biggest F1 calendar ever</p>

          {/* ── Username bar ── */}
          <div className="user-profile-bar">
            <label>ENTER USERNAME TO COMPETE:</label>
            <input
              type="text"
              placeholder="F1Fan_2026"
              value={username}
              onChange={e => handleUsernameChange(e.target.value)}
            />
            {username && <span className="paddock-pass">🏁 PADDOCK PASS ACTIVE</span>}
          </div>
        </div>

        {/* ── Race grid ── */}
        <div className="calendar-grid">
          {races.map((race, i) => {
            const isNext = i === nextRaceIndex
            const isCompleted = !!actualResults[race.round]
            return (
              <div
                key={race.round}
                className={`race-card${isNext ? ' next-race' : ''}${isCompleted ? ' race-completed' : ''}`}
                style={{ animationDelay: `${i * 40}ms` }}
              >
                {/* Top strip — round + badges */}
                <div className="rc-header">
                  <span className="rc-round">R{String(race.round).padStart(2, '0')}</span>
                  <div className="rc-badges">
                    {isCompleted && <span className="badge badge-done">DONE</span>}
                    {isNext && <span className="badge badge-next">NEXT</span>}
                    {race.isSprint && <span className="badge badge-sprint">SPRINT</span>}
                  </div>
                </div>

                {/* Flag + name */}
                <div className="rc-identity">
                  <span className="rc-flag">{race.flag}</span>
                  <div>
                    <h3
                      className="rc-name"
                      onClick={() => setSelectedCircuit({ ...race, image: getCircuitImage(race.circuit), results: actualResults[race.round] })}
                    >
                      {race.name}
                    </h3>
                    <p
                      className="rc-circuit"
                      onClick={() => setSelectedCircuit({ ...race, image: getCircuitImage(race.circuit), results: actualResults[race.round] })}
                    >
                      {race.circuit}
                    </p>
                  </div>
                </div>

                {race.date && <p className="rc-date">📅 {race.date}</p>}

                {/* AI prediction block */}
                {race.prediction && (
                  <div className="rc-prediction">
                    <div className="rc-pred-header">
                      <span className="ai-label">AI PICK</span>
                      <span className="rc-winner">🏆 {race.prediction}</span>
                    </div>
                    {/* Win probability bars */}
                    {race.topProbs.length > 0 && (
                      <div className="rc-prob-bars">
                        {race.topProbs.map((p, j) => (
                          <div key={p.constructor} className="rc-prob-row">
                            <span className="rc-prob-team">{p.constructor}</span>
                            <div className="rc-prob-track">
                              <div
                                className="rc-prob-fill"
                                style={{
                                  width: `${(p.win_probability * 100).toFixed(0)}%`,
                                  opacity: 1 - j * 0.2,
                                }}
                              />
                            </div>
                            <span className="rc-prob-pct">{(p.win_probability * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {/* Podium pills */}
                    {race.podium && (
                      <div className="rc-podium-row">
                        {['P1', 'P2', 'P3'].map(pos => (
                          <div key={pos} className={`rc-podium-pill rc-podium-${pos.toLowerCase()}`}>
                            <span className="rc-podium-pos">{pos}</span>
                            <span className="rc-podium-team">{race.podium[pos]}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Actual result */}
                {actualResults[race.round] && (
                  <div className="rc-result">
                    <span className="result-label">🏁 FINAL RESULT</span>
                    <div className="rc-result-grid">
                      {actualResults[race.round].race_winner && (
                        <div className="rc-result-item">
                          <span className="rc-result-key">GP</span>
                          <span className="rc-result-val">{actualResults[race.round].race_winner}</span>
                        </div>
                      )}
                      {actualResults[race.round].team_winner && (
                        <div className="rc-result-item">
                          <span className="rc-result-key">TEAM</span>
                          <span className="rc-result-val">{actualResults[race.round].team_winner}</span>
                        </div>
                      )}
                      {actualResults[race.round].qualy_winner && (
                        <div className="rc-result-item">
                          <span className="rc-result-key">POLE</span>
                          <span className="rc-result-val">{actualResults[race.round].qualy_winner}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* User prediction panel — only on next race */}
                {isNext && (
                  <div className="user-prediction-box">
                    <span className="user-label">WEEKEND FORECAST</span>
                    {[
                      { key: 'qualy', label: 'QUALY', placeholder: 'Pole Position...', list: allDrivers },
                      ...(race.isSprint ? [{ key: 'sprint', label: 'SPRINT', placeholder: 'Sprint Winner...', list: allDrivers }] : []),
                      { key: 'race', label: 'G_PRIX', placeholder: 'Race Winner...', list: allDrivers },
                      { key: 'team', label: 'TEAM', placeholder: 'Winning Team...', list: allTeams, isTeam: true },
                    ].map(({ key, label, placeholder, list, isTeam }) => (
                      <div key={key} className="prediction-row">
                        <label>{label}</label>
                        <select
                          value={userPredictions[race.round]?.[key] || ''}
                          onChange={e => handleUserPredict(race.round, key, e.target.value)}
                        >
                          <option value="">{placeholder}</option>
                          {list.map(item => {
                            const val = isTeam ? item : item.name
                            return <option key={val} value={val}>{val}</option>
                          })}
                        </select>
                      </div>
                    ))}
                    {userPredictions[race.round]?.race && race.prediction?.includes(userPredictions[race.round].race) && (
                      <div className="user-voted-name">
                        <span className="match-badge">✨ AI MATCH</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Circuit watermark */}
                <img
                  className="circuit-map"
                  src={getCircuitImage(race.circuit)}
                  alt={`${race.circuit} map`}
                  onError={e => { e.target.style.display = 'none' }}
                />
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Circuit modal ── */}
      {selectedCircuit && (
        <div className="circuit-modal" onClick={() => setSelectedCircuit(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setSelectedCircuit(null)}>×</button>
            <div className="modal-header">
              <div className="modal-header-top">
                <span className="modal-round">ROUND {String(selectedCircuit.round).padStart(2, '0')}</span>
                {selectedCircuit.results && <span className="completed-badge">COMPLETED</span>}
              </div>
              <div className="modal-title-row">
                <span className="modal-flag">{selectedCircuit.flag}</span>
                <h2 className="modal-title">{selectedCircuit.name}</h2>
              </div>
              <p className="modal-circuit">{selectedCircuit.circuit}</p>
            </div>
            <div className="modal-image-container">
              <img src={selectedCircuit.image} alt={selectedCircuit.circuit} />
            </div>
            <div className="modal-footer">
              <div className="modal-footer-stats">
                <p>📅 {selectedCircuit.date}</p>
                {selectedCircuit.prediction && (
                  <div className="modal-prediction">
                    <span className="ai-label">AI PICK</span>
                    <span style={{ fontWeight: 800, marginLeft: 8 }}>🏆 {selectedCircuit.prediction}</span>
                    {selectedCircuit.podium && (
                      <div className="rc-podium-row" style={{ marginTop: 10 }}>
                        {['P1', 'P2', 'P3'].map(pos => (
                          <div key={pos} className={`rc-podium-pill rc-podium-${pos.toLowerCase()}`}>
                            <span className="rc-podium-pos">{pos}</span>
                            <span className="rc-podium-team">{selectedCircuit.podium[pos]}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              {selectedCircuit.results && (
                <div className="modal-actual-results">
                  <span className="result-label">🏁 FINAL PODIUM</span>
                  <div className="modal-result-grid">
                    {selectedCircuit.results.race_winner && (
                      <div className="modal-result-item"><label>WINNER</label><span>{selectedCircuit.results.race_winner}</span></div>
                    )}
                    {selectedCircuit.results.qualy_winner && (
                      <div className="modal-result-item"><label>POLE</label><span>{selectedCircuit.results.qualy_winner}</span></div>
                    )}
                    {selectedCircuit.results.team_winner && (
                      <div className="modal-result-item"><label>TEAM</label><span>{selectedCircuit.results.team_winner}</span></div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default RaceCalendar