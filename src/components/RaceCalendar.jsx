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

    // Sync to Supabase if username exists
    if (username) {
      syncPredictionToSupabase(round, newRoundPreds);
    }
  }

  const syncPredictionToSupabase = async (round, predictions) => {
    try {
      // 1. Ensure user exists in leaderboard
      const { error: userError } = await supabase
        .from('leaderboard')
        .upsert({ username, joined_at: new Date().toISOString() }, { onConflict: 'username' });

      if (userError) throw userError;

      // 2. Add/Update prediction
      const { error: predError } = await supabase
        .from('predictions')
        .upsert({ 
          username, 
          round, 
          predictions, 
          created_at: new Date().toISOString() 
        }, { onConflict: 'username,round' });

      if (predError) throw predError;
      
      notify('Prediction saved successfully!', 'success');
    } catch (error) {
      console.error('Supabase Sync Detailed Error:', error);
      notify(`Sync Failed: ${error.message}`, 'error');
    }
  }

  const handleUsernameChange = (val) => {
    setUsername(val)
    localStorage.setItem('f1_username', val)
  }

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

  // Subscribe to actual results from Supabase (Real-time)
  useEffect(() => {
    // 1. Initial fetch
    const fetchResults = async () => {
      const { data } = await supabase.from('actual_results').select('*');
      if (data) {
        const resultsMap = data.reduce((acc, curr) => {
          acc[curr.round] = curr;
          return acc;
        }, {});
        setActualResults(resultsMap);
      }
    };
    fetchResults();

    // 2. Real-time subscription
    const channel = supabase
      .channel('results_realtime')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'actual_results' 
      }, (payload) => {
        setActualResults(prev => ({
          ...prev,
          [payload.new.round]: payload.new
        }));
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

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
            // Handles both normal hyphens and en-dashes (–) from the calendar data
            const parts = staticRace.date.split(/[–-]/);
            let endDay = parts.length > 1 ? parts[1].trim() : parts[0];
            // Extract only the numeric day
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
            name: staticRace.name || r.name,
            circuit: staticRace.circuit || r.circuit,
            date: staticRace.date || '',
            flag: staticRace.flag || '',
            prediction: r.predictedWinner ? `🏆 ${r.predictedWinner}` : 'Prediction unavailable',
            isSprint: staticRace.isSprint || false,
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
          
          <div className="user-profile-bar fade-in">
            <label>ENTER USERNAME TO COMPETE:</label>
            <input 
              type="text" 
              placeholder="F1Fan_2026" 
              value={username}
              onChange={(e) => handleUsernameChange(e.target.value)}
            />
            {username && <span className="paddock-pass">🏁 PADDOCK PASS ACTIVE</span>}
          </div>
        </div>
        <div className="calendar-grid">
          {races.map((race, i) => (
            <div
              key={race.round}
              className={`race-card ${i === nextRaceIndex ? 'next-race' : ''}`}
              style={{ transitionDelay: `${i * 50}ms` }}
            >
              <div className="race-card-header">
                <div className="race-round">ROUND {String(race.round).padStart(2, '0')}</div>
                <div className="race-status-badges">
                  {i === nextRaceIndex && <span className="next-race-badge">NEXT RACE</span>}
                  {race.isSprint && <span className="sprint-badge">SPRINT</span>}
                </div>
              </div>
              <span className="race-flag">{race.flag}</span>
              <h3 className="race-name">{race.name}</h3>
              <p className="race-circuit">{race.circuit}</p>
              {race.date && <p className="race-date">📅 {race.date}</p>}
              <div className="race-prediction">
                <span className="ai-label">AI PICK</span>
                {race.prediction}
              </div>
              
              {actualResults[race.round] && (
                <div className="actual-result-highlighter">
                  <span className="result-label">🏁 FINAL RESULT</span>
                  <div className="result-winners">
                    {actualResults[race.round].race_winner && <p>GP: <span>{actualResults[race.round].race_winner}</span></p>}
                    {actualResults[race.round].team_winner && <p>Team: <span>{actualResults[race.round].team_winner}</span></p>}
                    {actualResults[race.round].qualy_winner && <p>Pole: <span>{actualResults[race.round].qualy_winner}</span></p>}
                  </div>
                </div>
              )}
              
              {i === nextRaceIndex && (
                <div className="user-prediction-box">
                  <span className="user-label">WEEKEND FORECAST</span>
                  
                  <div className="prediction-row">
                    <label>QUALY</label>
                    <select 
                      value={userPredictions[race.round]?.qualy || ''} 
                      onChange={(e) => handleUserPredict(race.round, 'qualy', e.target.value)}
                    >
                      <option value="">Pole Position...</option>
                      {allDrivers.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
                    </select>
                  </div>

                  {race.isSprint && (
                    <div className="prediction-row">
                      <label>S_RACE</label>
                      <select 
                        value={userPredictions[race.round]?.sprint || ''} 
                        onChange={(e) => handleUserPredict(race.round, 'sprint', e.target.value)}
                      >
                        <option value="">Sprint Winner...</option>
                        {allDrivers.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
                      </select>
                    </div>
                  )}

                  <div className="prediction-row">
                    <label>G_PRIX</label>
                    <select 
                      value={userPredictions[race.round]?.race || ''} 
                      onChange={(e) => handleUserPredict(race.round, 'race', e.target.value)}
                    >
                      <option value="">Race Winner...</option>
                      {allDrivers.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
                    </select>
                  </div>

                  <div className="prediction-row">
                    <label>TEAM</label>
                    <select 
                      value={userPredictions[race.round]?.team || ''} 
                      onChange={(e) => handleUserPredict(race.round, 'team', e.target.value)}
                    >
                      <option value="">Winning Team...</option>
                      {allTeams.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>

                  {userPredictions[race.round]?.race && race.prediction.includes(userPredictions[race.round].race) && (
                    <div className="user-voted-name">
                      <span className="match-badge">✨ AI MATCH</span>
                    </div>
                  )}
                </div>
              )}
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
