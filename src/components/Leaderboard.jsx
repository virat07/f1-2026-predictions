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
            <div className="loading">
              <div className="spinner"></div>
              <p>Syncing Paddock Data...</p>
            </div>
          ) : (
            <div className="leaderboard-layout">
              {/* Podium for Top 3 */}
              <div className="leaderboard-podium">
                {data.users.slice(0, 3).map((user, idx) => (
                  <div key={user.username} className={`podium-item pos-${idx + 1}`}>
                    <div className="podium-rank">
                      {idx === 0 ? '🏆' : idx === 1 ? '🥈' : '🥉'}
                    </div>
                    <div className="user-avatar-large">
                      {user.username.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="podium-info">
                      <div className="podium-username">@{user.username}</div>
                      <div className="podium-score">{user.score} <span>PTS</span></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="leaderboard-main-content">
                <div className="standings-column">
                  <h3>Championship Standings</h3>
                  <div className="standings-list">
                    {data.users.slice(3).map((user, idx) => (
                      <div key={user.username} className="user-standing-row">
                        <div className="row-rank">#{idx + 4}</div>
                        <div className="user-avatar-small">
                          {user.username.substring(0, 1).toUpperCase()}
                        </div>
                        <div className="row-username">{user.username}</div>
                        <div className="row-score">{user.score} <span className="pts-label">PTS</span></div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="recent-activity-column">
                  <h3>Recent Paddock Activity</h3>
                  <div className="activity-list">
                    {data.predictions.map((pred, i) => (
                      <div key={i} className="activity-card">
                        <div className="activity-header">
                          <span className="activity-user">@{pred.username}</span>
                          <span className="activity-round">ROUND {pred.round}</span>
                        </div>
                        <div className="activity-grid">
                          <div className="activity-item">
                            <label>POLE</label>
                            <span>{pred.predictions?.qualy || '--'}</span>
                          </div>
                          <div className="activity-item highlight">
                            <label>WINNER</label>
                            <span>{pred.predictions?.race || '--'}</span>
                          </div>
                          <div className="activity-item">
                            <label>TEAM</label>
                            <span>{pred.predictions?.team || '--'}</span>
                          </div>
                        </div>
                        <div className="activity-time">
                          {new Date(pred.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default Leaderboard
