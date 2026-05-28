import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useApp } from '../store'
import { tLab } from '../i18n'
import { api } from '../api'

const C = {
  bg: '#060a0f',
  surface: '#0a0e17',
  accent: '#00ff88',
  accentDim: 'rgba(0,255,136,0.08)',
  accentBorder: 'rgba(0,255,136,0.22)',
  purple: '#6366f1',
  purpleDim: 'rgba(99,102,241,0.08)',
  blue: '#3b82f6',
  blueDim: 'rgba(59,130,246,0.08)',
  orange: '#f59e0b',
  orangeDim: 'rgba(245,158,11,0.08)',
  red: '#ef4444',
  gold: '#fbbf24',
  text: '#e2e8f0',
  sub: '#94a3b8',
  muted: '#475569',
  border: 'rgba(255,255,255,0.06)',
}

const DIFF = {
  easy:   '#10b981',
  medium: '#f59e0b',
  hard:   '#ef4444',
  expert: '#6366f1',
}

const CAT_COLOR = {
  smishing:        '#f59e0b',
  phishing:        '#3b82f6',
  'spear-phishing':'#6366f1',
  vishing:         '#10b981',
  osint:           '#00ff88',
  pretexting:      '#ec4899',
}

function StatCard({ label, value, color, bg, border }) {
  return (
    <div style={{
      background: bg,
      border: `1px solid ${border}`,
      borderRadius: 8,
      padding: '14px 16px',
    }}>
      <div style={{ fontSize: 8, fontWeight: 700, color: C.muted, letterSpacing: 2, marginBottom: 10 }}>
        {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color, lineHeight: 1, fontFamily: 'JetBrains Mono, monospace' }}>
        {value}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { locale, user } = useApp()
  const navigate = useNavigate()

  const [labs, setLabs] = useState([])
  const [progress, setProgress] = useState({ score: 0, completed: 0 })

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    api.getLabs().then(d => setLabs(d.labs || [])).catch(() => {})
  }, [user])

  return (
    <div style={{
      padding: '22px 24px',
      maxWidth: 1060,
      margin: '0 auto',
      fontFamily: 'JetBrains Mono, monospace',
    }}>

      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 8, fontWeight: 700, color: C.muted, letterSpacing: 2, marginBottom: 5 }}>
            OPERATOR TERMINAL
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 20, fontWeight: 800, color: C.text }}>{user?.username}</span>
            <span style={{ fontSize: 9, color: C.accent, letterSpacing: 1 }}>
              <span style={{
                display: 'inline-block', width: 6, height: 6, borderRadius: '50%',
                background: C.accent, marginRight: 5,
                boxShadow: `0 0 6px ${C.accent}`,
                verticalAlign: 'middle',
              }} />
              SESSION ACTIVE
            </span>
          </div>
        </div>
        <div style={{ fontSize: 9, color: C.muted, textAlign: 'right' }}>
          <div>{new Date().toISOString().slice(0, 10)}</div>
          <div style={{ color: C.sub, marginTop: 2 }}>SOCIALFORGE v1.0</div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginBottom: 24 }}>
        <StatCard label="COMPLETED" value={progress.completed} color={C.blue} bg={C.blueDim} border="rgba(59,130,246,0.22)" />
        <StatCard label="AVAILABLE" value={labs.length} color={C.orange} bg={C.orangeDim} border="rgba(245,158,11,0.22)" />
      </div>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 260px', gap: 18, alignItems: 'start' }}>

        {/* Labs section */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: C.muted, letterSpacing: 2 }}>TRAINING MODULES</div>
            <Link to="/labs" style={{
              fontSize: 9, color: C.accent, textDecoration: 'none', letterSpacing: 1, fontWeight: 700,
            }}>
              VIEW ALL →
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
            {labs.slice(0, 6).map(lab => {
              const diff = (lab.difficulty || 'easy').toLowerCase()
              const diffColor = DIFF[diff] || C.muted
              const cat = lab.category || ''
              const catColor = CAT_COLOR[cat] || C.sub
              const title = tLab(lab.title || lab.name, locale) || lab.id
              const desc = tLab(lab.description, locale) || ''
              return (
                <div
                  key={lab.id}
                  onClick={() => navigate(`/labs/${lab.id}`)}
                  style={{
                    background: 'rgba(255,255,255,0.018)',
                    border: `1px solid ${C.border}`,
                    borderLeft: `3px solid ${diffColor}`,
                    borderRadius: 8,
                    padding: '12px 14px',
                    cursor: 'pointer',
                    transition: 'background 0.12s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.035)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.018)' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 5 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: C.text, flex: 1, lineHeight: 1.3 }}>
                      {title}
                    </div>
                    <span style={{
                      fontSize: 7, fontWeight: 700, letterSpacing: 1, padding: '2px 6px', borderRadius: 3,
                      background: `${diffColor}18`, color: diffColor, border: `1px solid ${diffColor}35`,
                      marginLeft: 8, flexShrink: 0,
                    }}>
                      {diff.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.5, marginBottom: 8 }}>
                    {desc.slice(0, 72)}{desc.length > 72 ? '…' : ''}
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 9, alignItems: 'center' }}>
                    <span style={{ color: C.muted }}>{lab.estimated_time}</span>
                    {cat && (
                      <span style={{
                        fontSize: 7, fontWeight: 700, letterSpacing: 1, padding: '1px 5px', borderRadius: 3,
                        background: `${catColor}15`, color: catColor, border: `1px solid ${catColor}30`,
                      }}>
                        {cat.toUpperCase()}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

          {/* Quick links */}
          <div>
            <div style={{ fontSize: 9, fontWeight: 700, color: C.muted, letterSpacing: 2, marginBottom: 10 }}>
              QUICK ACCESS
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                { label: 'All Labs', path: '/labs', color: C.accent },
                { label: 'Settings', path: '/settings', color: C.blue },
              ].map(({ label, path, color }) => (
                <div
                  key={path}
                  onClick={() => navigate(path)}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    background: 'rgba(255,255,255,0.018)',
                    border: `1px solid ${C.border}`,
                    borderLeft: `3px solid ${color}`,
                    borderRadius: 6,
                    padding: '8px 12px',
                    cursor: 'pointer',
                    fontSize: 11, color: C.sub,
                    transition: 'background 0.12s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.035)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.018)' }}
                >
                  <span>{label}</span>
                  <span style={{ color: C.muted }}>→</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
