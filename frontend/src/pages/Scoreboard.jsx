import { useState, useEffect } from 'react'
import { useApp } from '../store'
import { t } from '../i18n'
import { api } from '../api'
import { Trophy, Medal } from 'lucide-react'

export default function Scoreboard() {
  const { locale } = useApp()
  const tr = (key) => t(key, locale)
  const [board, setBoard] = useState([])

  useEffect(() => {
    api.getScoreboard().then(d => setBoard(d.scoreboard)).catch(() => {})
  }, [])

  const rankColors = ['var(--orange)', 'var(--text-secondary)', '#cd7f32']

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: 800 }}>
      <h1 className="mono" style={{ fontSize: 28, marginBottom: 32, color: 'var(--accent)' }}>
        {'> '}{tr('scoreboard.title')}
      </h1>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-input)' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, width: 60 }}>
                {tr('scoreboard.rank')}
              </th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1 }}>
                {tr('scoreboard.player')}
              </th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, width: 100 }}>
                {tr('scoreboard.score')}
              </th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, width: 80 }}>
                {tr('scoreboard.labs')}
              </th>
            </tr>
          </thead>
          <tbody>
            {board.map((row) => (
              <tr key={row.rank} style={{
                borderBottom: '1px solid var(--border)',
                background: row.rank <= 3 ? 'rgba(255,255,255,0.02)' : 'transparent',
              }}>
                <td style={{ padding: '14px 16px' }}>
                  {row.rank <= 3 ? (
                    <Trophy size={16} color={rankColors[row.rank - 1]} />
                  ) : (
                    <span className="mono" style={{ color: 'var(--text-muted)', fontSize: 13 }}>#{row.rank}</span>
                  )}
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{ fontWeight: 500 }}>{row.display_name || row.username}</span>
                  <span className="mono" style={{ color: 'var(--text-muted)', fontSize: 12, marginLeft: 8 }}>@{row.username}</span>
                </td>
                <td className="mono" style={{ padding: '14px 16px', textAlign: 'right', color: 'var(--accent)', fontWeight: 600 }}>
                  {row.score}
                </td>
                <td style={{ padding: '14px 16px', textAlign: 'right', color: 'var(--text-muted)', fontSize: 13 }}>
                  {row.labs_completed}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {board.length === 0 && (
          <div style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
            <Medal size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
            <p style={{ fontSize: 14 }}>No players yet. Be the first!</p>
          </div>
        )}
      </div>
    </div>
  )
}
