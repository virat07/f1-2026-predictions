import { useEffect, useState } from 'react'
import { supabase } from '../utils/supabaseClient'
import './Leaderboard.css'

function Leaderboard() {
  const [data, setData] = useState({ users: [], predictions: [] })
  const [loading, setLoading] = useState(true)

  const fetchLeaderboard = async () => {
    try {
      const { data: users, error: userError } = await supabase
        .from('leaderboard')
        .select('*')
        .order('score', { ascending: false });

      const { data: predictions, error: predError } = await supabase
        .from('predictions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10);

      if (!userError && !predError) {
        setData({ users: users || [], predictions: predictions || [] });
      }
    } catch (err) {
      console.error('Supabase fetch failed', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLeaderboard()
    const interval = setInterval(fetchLeaderboard, 10000) // update every 10s
    return () => clearInterval(interval)
  }, [])

  return (
    <section id="leaderboard" className="section">
      <div className="container">
        <div className="section-header">
          <span className="section-tag">COMMUNITY</span>
          <h2 className="section-title">Global <span className="accent">Leaderboard</span></h2>
          <p className="section-subtitle">See what other fans are predicting for the 2026 season</p>
        </div>

        <div className="leaderboard-container">
          {loading ? (
            <div className="loading">Loading standings...</div>
          ) : (
            <>
              <div className="user-stats-grid">
                {data.users.sort((a,b) => b.score - a.score).map((user, idx) => (
                  <div key={user.username} className="user-rank-card">
                    <div className="rank-number">#{idx + 1}</div>
                    <div className="user-info">
                      <div className="username">{user.username}</div>
                      <div className="user-joined">Since {new Date(user.joined_at).toLocaleDateString()}</div>
                    </div>
                    <div className="user-score">{user.score} <span>pts</span></div>
                  </div>
                ))}
              </div>

              <div className="predictions-table-container">
                <h3>Recent Predictions</h3>
                <div className="table-responsive">
                  <table className="predictions-table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Round</th>
                        <th>Qualy (Pole)</th>
                        <th>Sprint Winner</th>
                        <th>Grand Prix</th>
                        <th>Winner (Team)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.predictions.map((pred, i) => (
                        <tr key={i}>
                          <td className="user-cell">@{pred.username}</td>
                          <td>R{pred.round}</td>
                          <td className="driver-cell">{pred.predictions?.qualy || '--'}</td>
                          <td className="driver-cell">{pred.predictions?.sprint || '--'}</td>
                          <td className="driver-cell highlight">{pred.predictions?.race || '--'}</td>
                          <td className="driver-cell">{pred.predictions?.team || '--'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  )
}

export default Leaderboard
