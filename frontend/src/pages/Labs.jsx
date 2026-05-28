import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../store'
import { tLab } from '../i18n'
import { api } from '../api'
import { Target, ChevronRight, Zap, RotateCw, Radio } from 'lucide-react'

const C = {
  bg:       '#060a0f',
  surface:  '#0b0f0b',
  border:   'rgba(0,255,136,0.09)',
  accent:   '#00ff88',
  red:      '#ff3366',
  orange:   '#f97316',
  purple:   '#a855f7',
  gold:     '#fbbf24',
  text:     '#d4f5e2',
  textDim:  'rgba(212,245,226,0.5)',
  muted:    'rgba(0,255,136,0.35)',
}

const DIFF = {
  easy:   { color: '#10b981', label: 'EASY'   },
  medium: { color: '#f97316', label: 'MEDIUM' },
  hard:   { color: '#ef4444', label: 'HARD'   },
}

const CAT = {
  vishing:  { icon: '📞', color: C.purple },
  phishing: { icon: '🎣', color: '#60a5fa' },
  smishing: { icon: '📱', color: C.orange  },
}

function SH({ children, color = C.muted }) {
  return (
    <div style={{
      fontSize: 9, fontWeight: 700, color, letterSpacing: 2.5,
      marginBottom: 14, textTransform: 'uppercase',
      display: 'flex', alignItems: 'center', gap: 8,
    }}>
      {children}
    </div>
  )
}

function Dot({ color, sz = 5, anim }) {
  return (
    <span style={{
      display: 'inline-block', width: sz, height: sz, borderRadius: '50%',
      background: color, boxShadow: `0 0 5px ${color}`,
      animation: anim ? 'rtPulse 1.8s infinite' : 'none',
      flexShrink: 0,
    }} />
  )
}

function SimulationPanel({ userId, locale }) {
  const [status, setStatus] = useState(null)  // null=loading
  const [starting, setStarting] = useState(false)

  const loadStatus = useCallback(() => {
    api.sessionStatus(userId).then(setStatus).catch(() => setStatus({ active: false }))
  }, [userId])

  useEffect(() => { loadStatus() }, [loadStatus])

  const handleStart = async () => {
    setStarting(true)
    try {
      await api.startSessionAll(userId)
      await loadStatus()
    } catch (e) {
      console.error(e)
    } finally {
      setStarting(false)
    }
  }

  const isLive = status?.active

  const panelStyle = {
    marginBottom: 28,
    borderRadius: 8,
    padding: '20px 24px',
    background: isLive
      ? 'linear-gradient(135deg, rgba(0,255,136,0.04) 0%, rgba(0,255,136,0.01) 100%)'
      : 'rgba(255,255,255,0.015)',
    border: `1px solid ${isLive ? 'rgba(0,255,136,0.22)' : 'rgba(255,255,255,0.06)'}`,
    borderLeft: `3px solid ${isLive ? C.accent : 'rgba(255,255,255,0.08)'}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 20,
    flexWrap: 'wrap',
    fontFamily: 'JetBrains Mono, monospace',
  }

  if (status === null) return (
    <div style={panelStyle}>
      <div style={{ fontSize: 9, color: C.muted, letterSpacing: 2 }}>LOADING SIMULATION STATUS…</div>
    </div>
  )

  const fmtUptime = (iso) => {
    if (!iso) return ''
    const secs = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
    const h = Math.floor(secs / 3600)
    const m = Math.floor((secs % 3600) / 60)
    if (h > 0) return `${h}h ${m}m`
    return `${m}m`
  }

  return (
    <div style={panelStyle}>
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Status row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            fontSize: 9, fontWeight: 700, letterSpacing: 2.5,
            color: isLive ? C.accent : 'rgba(255,255,255,0.25)',
          }}>
            {isLive
              ? <><Radio size={10} color={C.accent} style={{ animation: 'rtPulse 1.8s infinite' }} /> SIMULATION LIVE</>
              : <><span style={{ opacity: 0.4 }}>◎</span> SIMULATION OFFLINE</>
            }
          </div>
          {isLive && (
            <span style={{ fontSize: 8, color: C.muted, letterSpacing: 1 }}>
              uptime: {fmtUptime(status.started_at)}
            </span>
          )}
        </div>

        {/* Info row */}
        {isLive ? (
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 10, color: C.textDim }}>
              <span style={{ color: C.accent, fontWeight: 700 }}>{status.total_npcs}</span>
              {' '}{locale === 'ru' ? 'НПС активно' : 'NPCs active'}
            </span>
            <span style={{ fontSize: 10, color: C.textDim }}>
              <span style={{ color: C.muted, fontWeight: 700 }}>{status.total_sessions}</span>
              {' '}{locale === 'ru' ? 'сессий' : 'sessions'}
            </span>
            <span style={{ fontSize: 9, color: 'rgba(0,255,136,0.2)', letterSpacing: 1 }}>
              SEED #{status.daily_seed}
            </span>
          </div>
        ) : (
          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)', lineHeight: 1.6 }}>
            {locale === 'ru'
              ? 'НПС бездействуют. Запусти симуляцию — они оживут и забудут вчерашний день.'
              : 'NPCs are idle. Start the simulation — they come alive with fresh daily contexts.'}
          </div>
        )}
      </div>

      {/* Button */}
      <button
        onClick={handleStart}
        disabled={starting}
        style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '10px 20px', borderRadius: 6,
          background: isLive
            ? 'rgba(255,255,255,0.04)'
            : 'rgba(0,255,136,0.1)',
          border: isLive
            ? '1px solid rgba(255,255,255,0.1)'
            : `1px solid ${C.accent}44`,
          color: isLive ? C.textDim : C.accent,
          fontSize: 10, fontWeight: 700, letterSpacing: 1.5,
          cursor: starting ? 'wait' : 'pointer',
          fontFamily: 'JetBrains Mono, monospace',
          transition: 'all 0.15s',
          flexShrink: 0,
          opacity: starting ? 0.6 : 1,
          boxShadow: (!isLive && !starting) ? `0 0 18px rgba(0,255,136,0.12)` : 'none',
        }}
      >
        {starting
          ? <><RotateCw size={12} style={{ animation: 'spin 1s linear infinite' }} /> {locale === 'ru' ? 'ЗАПУСК…' : 'STARTING…'}</>
          : isLive
            ? <><RotateCw size={12} /> {locale === 'ru' ? 'НОВЫЙ ДЕНЬ' : 'RESTART DAY'}</>
            : <><Zap size={12} /> {locale === 'ru' ? 'ЗАПУСТИТЬ СИМУЛЯЦИЮ' : 'START SIMULATION'}</>
        }
      </button>
    </div>
  )
}

function LabCard({ lab, locale, onClick }) {
  const [hov, setHov] = useState(false)
  const diff    = DIFF[lab.difficulty] || DIFF.medium
  const cat     = CAT[lab.category]   || { icon: '⚡', color: C.accent }
  const isReal  = lab.type === 'operation'
  const inProg  = lab.status === 'in_progress'
  const done    = lab.status === 'completed'
  const title   = tLab(lab.title, locale)
  const desc    = tLab(lab.description, locale)

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background:   hov ? 'rgba(0,255,136,0.035)' : 'rgba(0,255,136,0.015)',
        border:       `1px solid ${hov ? 'rgba(0,255,136,0.28)' : C.border}`,
        borderLeft:   `3px solid ${hov ? C.accent : isReal ? C.red : 'rgba(0,255,136,0.35)'}`,
        borderRadius: 7,
        padding:      '15px 18px',
        cursor:       'pointer',
        transition:   'all 0.15s',
        boxShadow:    hov ? '0 0 24px rgba(0,255,136,0.09), 0 2px 12px rgba(0,0,0,0.4)' : 'none',
        position:     'relative', overflow: 'hidden',
        fontFamily:   'JetBrains Mono, monospace',
      }}
    >
      {isReal && !inProg && !done && (
        <div style={{
          position: 'absolute', top: 9, right: 10,
          fontSize: 7, fontWeight: 700, letterSpacing: 2,
          color: 'rgba(255,51,102,0.3)',
        }}>OPERATION</div>
      )}
      {inProg && (
        <div style={{
          position: 'absolute', top: 8, right: 10,
          fontSize: 7, fontWeight: 700, letterSpacing: 1.5, padding: '2px 6px', borderRadius: 3,
          background: 'rgba(249,115,22,0.1)', border: '1px solid rgba(249,115,22,0.3)',
          color: C.orange,
        }}>IN PROGRESS</div>
      )}
      {done && (
        <div style={{
          position: 'absolute', top: 8, right: 10,
          fontSize: 7, fontWeight: 700, letterSpacing: 1.5, padding: '2px 6px', borderRadius: 3,
          background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.3)',
          color: C.accent,
        }}>✓ DONE</div>
      )}

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 8, gap: 10 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 8, color: cat.color, letterSpacing: 1.5, marginBottom: 5, fontWeight: 700 }}>
            {cat.icon} {(lab.category || 'operation').toUpperCase()}
          </div>
          <div style={{
            fontSize: 13.5, fontWeight: 700,
            color: hov ? C.accent : C.text,
            lineHeight: 1.35, transition: 'color 0.15s',
          }}>
            {title}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 5, flexShrink: 0 }}>
          <span style={{
            fontSize: 8, fontWeight: 700, letterSpacing: 1,
            padding: '2px 7px', borderRadius: 3,
            background: `${diff.color}15`, color: diff.color,
            border: `1px solid ${diff.color}30`,
          }}>{diff.label}</span>
        </div>
      </div>

      <div style={{ fontSize: 11, color: C.textDim, lineHeight: 1.7, marginBottom: 12 }}>
        {desc}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: 14, fontSize: 9, color: C.muted }}>
          <span>⏱ {lab.estimated_time}</span>
        </div>
        <ChevronRight
          size={13}
          color={hov ? C.accent : 'transparent'}
          style={{ transition: 'transform 0.15s', transform: hov ? 'translateX(3px)' : 'translateX(0)' }}
        />
      </div>
    </div>
  )
}

export default function Labs() {
  const { locale, user } = useApp()
  const navigate = useNavigate()
  const [labs, setLabs] = useState([])

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    api.getLabs().then(d => setLabs(d.labs)).catch(() => {})
  }, [user])

  const fullLabs  = labs.filter(l => l.type === 'operation')
  const miniLabs  = labs.filter(l => l.type !== 'operation')
  const totalPts  = labs.reduce((s, l) => s + (l.points || 0), 0)
  const realCount = fullLabs.length

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      background: C.bg,
      fontFamily: 'JetBrains Mono, monospace',
      padding: '32px 28px',
    }}>
      <style>{`
        @keyframes rtPulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
      `}</style>

      <div style={{ maxWidth: 1100, margin: '0 auto' }}>

        {/* ── Page header ── */}
        <div style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10, fontSize: 9, color: 'rgba(0,255,136,0.3)', fontWeight: 700, letterSpacing: 1.5 }}>
            <span>SOCIALFORGE</span>
            <span style={{ color: 'rgba(0,255,136,0.15)' }}>//</span>
            <span style={{ color: C.accent }}>OPERATION CENTER</span>
            <span style={{ color: 'rgba(0,255,136,0.15)' }}>&gt;</span>
            <span style={{ color: C.text }}>MISSION SELECT</span>
          </div>
          <div style={{ fontSize: 23, fontWeight: 700, color: C.text, letterSpacing: 0.3 }}>
            {locale === 'ru' ? 'Выбор миссии' : 'Mission Select'}
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 5, marginBottom: 20 }}>
            {locale === 'ru'
              ? 'Атакуй. Социализируй. Захвати флаг.'
              : 'Attack. Socialize. Capture the flag.'}
          </div>
        </div>

        {/* ── Simulation Panel ── */}
        {user && <SimulationPanel userId={user.user_id} locale={locale} />}

        {/* ── Stats pills ── */}
        {labs.length > 0 && (
          <div style={{ display: 'flex', gap: 8, marginBottom: 30, flexWrap: 'wrap' }}>
            {[
              { label: locale === 'ru' ? 'МИССИЙ' : 'MISSIONS', value: labs.length, color: C.accent },
              { label: locale === 'ru' ? 'ОПЕРАЦИЙ' : 'OPERATIONS', value: realCount, color: C.red },
            ].map(stat => (
              <div key={stat.label} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '6px 14px', borderRadius: 6,
                background: `${stat.color}0d`,
                border: `1px solid ${stat.color}28`,
              }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: stat.color }}>{stat.value}</span>
                <span style={{ fontSize: 8, fontWeight: 700, letterSpacing: 2, color: `${stat.color}80` }}>
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* ── Full Operations ── */}
        {fullLabs.length > 0 && (
          <div style={{ marginBottom: 42 }}>
            <SH color={C.accent}>
              <Dot color={C.red} sz={5} anim />
              {locale === 'ru' ? 'Операции' : 'Operations'}
            </SH>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: 11 }}>
              {fullLabs.map(lab => (
                <LabCard key={lab.id} lab={lab} locale={locale} onClick={() => navigate(`/labs/${lab.id}`)} />
              ))}
            </div>
          </div>
        )}

        {/* ── Mini Labs / Drills ── */}
        {miniLabs.length > 0 && (
          <div>
            <SH color={C.textDim}>
              ◈&nbsp;{locale === 'ru' ? 'Тренировочные упражнения' : 'Training Drills'}
            </SH>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 10 }}>
              {miniLabs.map(lab => (
                <LabCard key={lab.id} lab={lab} locale={locale} onClick={() => navigate(`/labs/${lab.id}`)} />
              ))}
            </div>
          </div>
        )}

        {labs.length === 0 && (
          <div style={{ textAlign: 'center', padding: '90px 0', color: C.muted }}>
            <div style={{
              width: 56, height: 56, borderRadius: 10, margin: '0 auto 18px',
              background: 'rgba(0,255,136,0.04)',
              border: '1px solid rgba(0,255,136,0.12)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Target size={24} color={C.accent} style={{ opacity: 0.4, animation: 'rtPulse 2s infinite' }} />
            </div>
            <div style={{ fontSize: 10, letterSpacing: 2.5, fontWeight: 700, marginBottom: 8 }}>
              LOADING MISSION DOSSIERS…
            </div>
            <div style={{ fontSize: 9, color: 'rgba(0,255,136,0.2)', letterSpacing: 1 }}>
              {locale === 'ru' ? 'ПОДКЛЮЧЕНИЕ К СЕРВЕРУ ОПЕРАЦИЙ' : 'CONNECTING TO OPERATIONS SERVER'}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
