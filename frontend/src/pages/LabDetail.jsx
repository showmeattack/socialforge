import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useApp } from '../store'
import { t, tLab } from '../i18n'
import { api } from '../api'
import {
  Flag, CheckCircle, ExternalLink,
  Send, Globe, Phone, Mail, ArrowLeft,
  Building, Users, Copy, Check,
  Lock, Skull, Fish, MessageSquare,
} from 'lucide-react'

const C = {
  bg:       '#060a0f',
  surface:  '#0b100b',
  panel:    '#0d120d',
  border:   'rgba(0,255,136,0.09)',
  borderHot:'rgba(0,255,136,0.28)',
  accent:   '#00ff88',
  red:      '#ff3366',
  orange:   '#f97316',
  purple:   '#a855f7',
  blue:     '#60a5fa',
  gold:     '#fbbf24',
  text:     '#d4f5e2',
  textDim:  'rgba(212,245,226,0.5)',
  muted:    'rgba(0,255,136,0.35)',
}

function getGullColor(g) {
  if (!g) return C.muted
  if (g >= 70) return C.accent
  if (g >= 40) return C.orange
  return C.red
}

function PersonaAvatar({ name, gullibility, size = 30 }) {
  const initials = (name || '?').split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
  const color = getGullColor(gullibility)
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%', flexShrink: 0,
      background: `${color}15`,
      border: `1.5px solid ${color}50`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.34, fontWeight: 700, color,
      fontFamily: 'JetBrains Mono, monospace',
      boxShadow: `0 0 8px ${color}20`,
    }}>
      {initials}
    </div>
  )
}

function SH({ children, color = C.muted }) {
  return (
    <div style={{
      fontSize: 8, fontWeight: 700, color, letterSpacing: 2.5,
      marginBottom: 9, textTransform: 'uppercase',
    }}>
      {children}
    </div>
  )
}

function Dot({ color, anim }) {
  return (
    <span style={{
      display: 'inline-block', width: 6, height: 6, borderRadius: '50%',
      background: color, boxShadow: `0 0 4px ${color}`,
      animation: anim ? 'rtPulse 1.8s infinite' : 'none',
      flexShrink: 0,
    }} />
  )
}

function ToolBtn({ icon: Icon, label, color, href, disabled }) {
  const [hov, setHov] = useState(false)
  if (disabled) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5,
        padding: '10px 6px', borderRadius: 7,
        border: `1px solid rgba(255,255,255,0.05)`,
        background: 'rgba(255,255,255,0.015)',
        opacity: 0.32, cursor: 'not-allowed',
      }}>
        <Icon size={15} color={color} />
        <span style={{ fontSize: 9, color: C.textDim, fontWeight: 600 }}>{label}</span>
      </div>
    )
  }
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
      <div
        onMouseEnter={() => setHov(true)}
        onMouseLeave={() => setHov(false)}
        style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5,
          padding: '10px 6px', borderRadius: 7, cursor: 'pointer',
          border: `1px solid ${hov ? color + '55' : 'rgba(0,255,136,0.08)'}`,
          background: hov ? `${color}10` : 'rgba(0,255,136,0.02)',
          transition: 'all 0.14s',
          boxShadow: hov ? `0 0 12px ${color}22` : 'none',
        }}
      >
        <Icon size={15} color={hov ? color : C.textDim} style={{ transition: 'color 0.14s' }} />
        <span style={{ fontSize: 9, color: hov ? color : C.textDim, fontWeight: 600, transition: 'color 0.14s' }}>
          {label}
        </span>
        <ExternalLink size={7} color={hov ? color : 'transparent'} />
      </div>
    </a>
  )
}

export default function LabDetail() {
  const { labId } = useParams()
  const { locale, user } = useApp()
  const navigate = useNavigate()
  const tr = (key) => t(key, locale)

  const [lab,           setLab]           = useState(null)
  const [flagInputs,    setFlagInputs]    = useState({})
  const [flagResults,   setFlagResults]   = useState({})
  const [capturedFlags, setCapturedFlags] = useState(new Set())
  const [walkthroughRevealed, setWalkthroughRevealed] = useState(0)
  const [pendingWalkthrough,  setPendingWalkthrough]  = useState(false)

  const [labStatus,     setLabStatus]     = useState(null)
  const [failureInfo,   setFailureInfo]   = useState(null)
  const [bustDismissed, setBustDismissed] = useState(false)

  const [completionFlash,  setCompletionFlash]  = useState(false)
  const [showCompletion,   setShowCompletion]   = useState(false)
  const [prevStatus,       setPrevStatus]       = useState(null)
  const [explanation,      setExplanation]      = useState(null)

  const autoStarted   = useRef(false)
  const initialLoad   = useRef(true)

  const targetPort = lab?.target_company?.website_port || 9001
  const realUrl    = `http://127.0.0.1:${targetPort}`

  const isOperation = lab?.type === 'operation'

  function playCompletionSound() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      ;[523, 659, 784, 1047].forEach((freq, i) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.frequency.value = freq
        osc.type = 'sine'
        gain.gain.setValueAtTime(0.25, ctx.currentTime + i * 0.15)
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.15 + 0.35)
        osc.start(ctx.currentTime + i * 0.15)
        osc.stop(ctx.currentTime + i * 0.15 + 0.35)
      })
    } catch(e) {}
  }

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    api.getLab(labId).then(d => {
      setLab(d)
    }).catch(() => {
      alert(`Lab not found: "${labId}"`)
      navigate('/labs')
    })
    refreshStatus()
  }, [labId, user])

  const refreshStatus = async () => {
    if (!user) return
    try {
      const p = await api.getLabProgress(labId, user.user_id)
      const newStatus = p.status
      setLabStatus(newStatus)
      if (p.status === 'failed') setFailureInfo({ reason: p.failure_reason, persona: p.failed_persona })
      else { setFailureInfo(null); setBustDismissed(false) }
      if (p.flags_found?.length) setCapturedFlags(new Set(p.flags_found))

      const isFirstLoad = initialLoad.current
      initialLoad.current = false

      setPrevStatus(prev => {
        if (newStatus === 'completed' && prev !== 'completed' && !isFirstLoad) {
          playCompletionSound()
          setCompletionFlash(true)
          setTimeout(() => setCompletionFlash(false), 2500)
          setShowCompletion(true)
          if (!isOperation) {
            fetch(`/api/labs/${labId}/explanation?locale=${locale}`)
              .then(r => r.ok ? r.json() : null)
              .then(data => { if (data) setExplanation(data) })
              .catch(() => {})
          }
        }
        return newStatus
      })

      // Auto-start lab on first load if global simulation is active
      if (newStatus === 'not_started' && !autoStarted.current) {
        autoStarted.current = true
        const sim = await api.sessionStatus(user.user_id).catch(() => ({ active: false }))
        if (sim.active) {
          await api.startLab(labId, user.user_id).catch(() => {})
          const s = await api.currentSession(user.user_id, labId).catch(() => ({ session: null }))
          if (!s.session) await api.startSession(user.user_id, labId).catch(() => {})
          setLabStatus('in_progress')
        }
      }
    } catch (_) {}
  }





  const submitFlag = async (flagId) => {
    const value = flagInputs[flagId]?.trim()
    if (!value) return
    try {
      const res = await api.submitFlag({ user_id: user.user_id, lab_id: labId, flag_id: flagId, flag_value: value })
      setFlagResults(prev => ({ ...prev, [flagId]: res }))
      if (res.correct) {
        setCapturedFlags(prev => new Set([...prev, flagId]))
        await refreshStatus()
      }
    } catch (err) {
      setFlagResults(prev => ({ ...prev, [flagId]: { correct: false, message: err.message } }))
    }
  }

  if (!lab) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 'calc(100vh - 56px)', background: C.bg, fontFamily: 'JetBrains Mono, monospace' }}>
      <div style={{ fontSize: 11, color: C.muted, letterSpacing: 2 }}>LOADING DOSSIER…</div>
    </div>
  )

  const totalFlags       = lab.attack_chain?.filter(s => s.flag)?.length || 0
  const capturedCount    = capturedFlags.size
  const progressPercent  = totalFlags > 0 ? Math.round((capturedCount / totalFlags) * 100) : 0
  const isMiniLab        = totalFlags <= 1
  const companySlug      = lab.target_company?.company_slug

  const statusColor = labStatus === 'failed' ? C.red : labStatus === 'in_progress' ? C.accent : labStatus === 'completed' ? C.accent : C.blue
  const statusLabel = labStatus === 'failed'
    ? tr('lab.missionFailed')
    : labStatus === 'in_progress'
    ? (locale === 'ru' ? 'СИМУЛЯЦИЯ АКТИВНА' : 'SIMULATION ACTIVE')
    : labStatus === 'completed'
    ? tr('lab.missionComplete')
    : tr('lab.awaiting')

  const totalHintCost = lab.attack_chain?.flatMap(s => s.hints || []).reduce((sum, h) => sum + (h.cost || 0), 0) || 150
  const allFlagSteps = lab.attack_chain?.filter(s => s.flag) || []

  const personas = lab.personas ? Object.entries(lab.personas) : []

  const operationFlagId = lab?.operation_flag_id || lab?.attack_chain?.find(s => s.flag)?.flag?.id || 'flag_access'
  const operationFlagCaptured = capturedFlags.has(operationFlagId) || (isOperation && labStatus === 'completed')

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      background: C.bg,
      fontFamily: 'JetBrains Mono, monospace',
      color: C.text,
    }}>

      <style>{`
        @keyframes spin    { from { transform: rotate(0deg); }   to { transform: rotate(360deg); } }
@keyframes scan    { from { background-position: 0 0; }  to { background-position: 0 100px; } }
        @keyframes rtPulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
        @keyframes typingDot { 0%,80%,100%{opacity:0.2;transform:scale(0.8)} 40%{opacity:1;transform:scale(1.2)} }
        @keyframes gtaBust {
          0%   { transform: scale(4); opacity: 0; filter: blur(20px); }
          60%  { transform: scale(0.9); opacity: 1; filter: blur(0); }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes labFlash {
          0% { opacity: 0; }
          10% { opacity: 1; }
          80% { opacity: 1; }
          100% { opacity: 0; }
        }
      `}</style>

      {completionFlash && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 9999,
          background: 'rgba(0,255,136,0.06)',
          border: '2px solid #00ff88',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          pointerEvents: 'none',
          animation: 'labFlash 2.5s ease-out forwards',
        }}>
          <div style={{ fontSize: 32, fontWeight: 800, color: '#00ff88', letterSpacing: 4, fontFamily: 'JetBrains Mono,monospace' }}>
            MISSION COMPLETE
          </div>
          <div style={{ fontSize: 14, color: '#94a3b8', marginTop: 12, fontFamily: 'JetBrains Mono,monospace' }}>
            {lab?.title?.en || lab?.title || 'Lab'} — Objective Achieved
          </div>
        </div>
      )}

      {showCompletion && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 1001,
          background: 'rgba(0,8,4,0.93)',
          backdropFilter: 'blur(12px)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 40, textAlign: 'center', fontFamily: 'JetBrains Mono, monospace',
        }}>
          <div style={{ fontSize: 10, letterSpacing: 5, color: C.muted, marginBottom: 16 }}>OBJECTIVE ACHIEVED</div>
          <div style={{ fontSize: 52, fontWeight: 900, color: C.accent, letterSpacing: 6, textShadow: `0 0 40px ${C.accent}60` }}>
            MISSION<br/>COMPLETE
          </div>
          <div style={{ fontSize: 14, color: C.textDim, marginTop: 16 }}>
            {tLab(lab?.title, locale)}
          </div>
          <div style={{ display: 'flex', gap: 12, marginTop: 32 }}>
            <button
              onClick={() => navigate('/labs')}
              style={{
                padding: '12px 28px', fontSize: 12, borderRadius: 8,
                background: C.accent, color: '#000', border: 'none',
                cursor: 'pointer', fontWeight: 900, letterSpacing: 2,
                fontFamily: 'JetBrains Mono, monospace',
                boxShadow: `0 0 24px ${C.accent}40`,
              }}
            >→ NEXT MISSION</button>
            <button
              onClick={() => setShowCompletion(false)}
              style={{
                padding: '12px 28px', fontSize: 12, borderRadius: 8,
                background: 'rgba(255,255,255,0.06)', color: C.textDim,
                border: '1px solid rgba(255,255,255,0.1)',
                cursor: 'pointer', letterSpacing: 1,
                fontFamily: 'JetBrains Mono, monospace',
              }}
            >REVIEW MISSION</button>
          </div>
        </div>
      )}

      <div style={{ maxWidth: 1020, margin: '0 auto', padding: '22px 24px' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <button onClick={() => navigate('/labs')} style={{
            background: 'none', border: 'none', cursor: 'pointer', padding: '2px 4px',
            color: C.muted, display: 'flex', alignItems: 'center', gap: 4, fontSize: 10,
          }}>
            <ArrowLeft size={12} /> LABS
          </button>
          <span style={{ color: 'rgba(0,255,136,0.2)', fontSize: 10 }}>/</span>
          <span style={{ fontSize: 10, color: C.accent }}>{labId.toUpperCase()}</span>
          {isMiniLab && !isOperation && (
            <span style={{
              fontSize: 8, fontWeight: 700, padding: '2px 7px', borderRadius: 3, letterSpacing: 1,
              background: 'rgba(16,185,129,0.12)', color: '#10b981', border: '1px solid rgba(16,185,129,0.25)',
            }}>MINI</span>
          )}
          {isOperation && (
            <span style={{
              fontSize: 8, fontWeight: 700, padding: '2px 7px', borderRadius: 3, letterSpacing: 1,
              background: 'rgba(239,68,68,0.12)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.25)',
            }}>OPERATION</span>
          )}
        </div>

        <h2 style={{ fontSize: 19, fontWeight: 700, marginBottom: 7, color: C.text, letterSpacing: 0.3 }}>
          {tLab(lab.title, locale)}
        </h2>
        <p style={{ fontSize: 12, color: C.textDim, lineHeight: 1.7, marginBottom: 20, maxWidth: 680 }}>
          {tLab(lab.description, locale)}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 272px', gap: 18, alignItems: 'start' }}>

          <div>

            <div style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '11px 16px', borderRadius: 8, marginBottom: 18,
              background: `${statusColor}08`,
              border: `1px solid ${statusColor}28`,
              borderLeft: `3px solid ${statusColor}`,
            }}>
              <div style={{ flexShrink: 0 }}>
                {labStatus === 'failed'       && <Skull size={16} color={C.red} />}
                {labStatus === 'in_progress'  && <Dot color={C.accent} anim />}
                {labStatus === 'completed'    && <CheckCircle size={16} color={C.accent} />}
                {(!labStatus || labStatus === 'not_started') && <Lock size={14} color={C.blue} />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: statusColor, letterSpacing: 1.5, marginBottom: 3 }}>
                  {statusLabel}
                </div>
                <div style={{ fontSize: 10, color: C.textDim }}>
                  {labStatus === 'failed'
                    ? (failureInfo?.reason
                        ? `${failureInfo.reason}${failureInfo.persona ? ` — ${failureInfo.persona}` : ''} · ${locale === 'ru' ? 'Перезапусти симуляцию на странице Миссий.' : 'Restart simulation from Mission Select.'}`
                        : (locale === 'ru' ? 'Перезапусти симуляцию на странице Миссий.' : 'Restart simulation from Mission Select.'))
                    : labStatus === 'in_progress'
                    ? (locale === 'ru' ? 'НПС живут по расписанию — атакуй осторожно.' : 'NPCs live on schedule — attack carefully.')
                    : labStatus === 'completed'
                    ? (locale === 'ru' ? 'Все флаги захвачены.' : 'All flags captured.')
                    : (locale === 'ru' ? 'Симуляция выключена — запусти её на странице Миссий.' : 'Simulation offline — start it from Mission Select.')}
                </div>
              </div>
              {(labStatus === 'not_started' || !labStatus || labStatus === 'failed') && (
                <button onClick={() => navigate('/labs')} style={{
                  padding: '6px 13px', borderRadius: 6, cursor: 'pointer',
                  background: labStatus === 'failed' ? 'rgba(255,51,102,0.06)' : 'rgba(96,165,250,0.07)',
                  color: labStatus === 'failed' ? C.red : C.blue,
                  border: `1px solid ${labStatus === 'failed' ? 'rgba(255,51,102,0.2)' : 'rgba(96,165,250,0.2)'}`,
                  fontFamily: 'inherit', fontSize: 10, fontWeight: 700, letterSpacing: 1,
                  display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0, whiteSpace: 'nowrap',
                }}>
                  <ArrowLeft size={10} />
                  {locale === 'ru' ? 'К запуску' : 'Mission Select'}
                </button>
              )}
            </div>

            {lab.objective && (
              <div style={{
                padding: '12px 16px', borderRadius: 8, marginBottom: 18,
                background: 'rgba(96,165,250,0.06)',
                border: '1px solid rgba(96,165,250,0.2)',
                borderLeft: '3px solid rgba(96,165,250,0.6)',
              }}>
                <div style={{ fontSize: 8, fontWeight: 700, color: 'rgba(96,165,250,0.6)', letterSpacing: 2, marginBottom: 6 }}>
                  {tr('lab.objective')}
                </div>
                <div style={{ fontSize: 12.5, color: '#93c5fd', lineHeight: 1.6, fontWeight: 500 }}>
                  {tLab(lab.objective, locale)}
                </div>
              </div>
            )}

            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 8, fontWeight: 700, color: C.muted, letterSpacing: 2 }}>
                  {tr('lab.missionProgress')}
                </span>
                <span style={{ fontSize: 9, color: isOperation ? (operationFlagCaptured ? C.accent : C.muted) : (capturedCount > 0 ? C.accent : C.muted) }}>
                  {isOperation
                    ? `${operationFlagCaptured ? 1 : 0}/1 — ${operationFlagCaptured ? 100 : 0}%`
                    : `${capturedCount}/${totalFlags} — ${progressPercent}%`}
                </span>
              </div>
              <div style={{ height: 2, background: 'rgba(0,255,136,0.08)', borderRadius: 1, overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: isOperation ? (operationFlagCaptured ? '100%' : '0%') : `${progressPercent}%`,
                  background: `linear-gradient(90deg, ${C.accent}, #06d6a0)`,
                  transition: 'width 0.6s ease',
                  boxShadow: (isOperation ? operationFlagCaptured : capturedCount > 0) ? `0 0 8px ${C.accent}55` : 'none',
                }} />
              </div>
            </div>

            {isOperation ? (
              <div style={{ marginBottom: 20 }}>
                <SH color={C.muted}>{tr('lab.missionFlag')}</SH>
                <div style={{
                  display: 'flex', gap: 4, alignItems: 'center',
                  background: 'rgba(0,0,0,0.3)',
                  border: `1px solid ${flagResults[operationFlagId]?.correct ? C.accent : flagResults[operationFlagId] ? C.red : 'rgba(0,255,136,0.15)'}`,
                  borderRadius: 6, padding: '3px 4px 3px 10px',
                }}>
                  <span style={{ fontSize: 10, color: operationFlagCaptured ? C.accent : 'rgba(0,255,136,0.3)', flexShrink: 0 }}>$</span>
                  <input
                    placeholder="SF{...}"
                    value={flagInputs[operationFlagId] || ''}
                    onChange={e => setFlagInputs(prev => ({ ...prev, [operationFlagId]: e.target.value }))}
                    onKeyDown={e => e.key === 'Enter' && submitFlag(operationFlagId)}
                    disabled={operationFlagCaptured}
                    style={{
                      flex: 1, border: 'none', background: 'transparent',
                      fontSize: 11, padding: '7px 4px',
                      color: operationFlagCaptured ? C.accent : C.text,
                      fontFamily: 'JetBrains Mono, monospace', outline: 'none',
                    }}
                  />
                  <button onClick={() => submitFlag(operationFlagId)} disabled={operationFlagCaptured} style={{
                    padding: '6px 14px', borderRadius: 5,
                    background: operationFlagCaptured ? 'rgba(0,255,136,0.1)' : 'rgba(0,255,136,0.15)',
                    color: C.accent, border: '1px solid rgba(0,255,136,0.25)',
                    fontFamily: 'inherit', fontSize: 10, fontWeight: 700,
                    cursor: operationFlagCaptured ? 'default' : 'pointer',
                    display: 'flex', alignItems: 'center', gap: 5,
                  }}>
                    <Send size={10} />
                    SUBMIT
                  </button>
                </div>
                {flagResults[operationFlagId] && (
                  <div style={{
                    marginTop: 8, fontSize: 10, padding: '6px 12px', borderRadius: 5,
                    background: flagResults[operationFlagId].correct ? 'rgba(0,255,136,0.08)' : 'rgba(255,51,102,0.08)',
                    color: flagResults[operationFlagId].correct ? C.accent : C.red,
                    border: `1px solid ${flagResults[operationFlagId].correct ? 'rgba(0,255,136,0.2)' : 'rgba(255,51,102,0.2)'}`,
                  }}>
                    {flagResults[operationFlagId].correct
                      ? `✓ ${tr('lab.flagCorrect')}`
                      : `✗ ${tr('lab.flagWrong')}`}
                  </div>
                )}
              </div>
            ) : (
              allFlagSteps.length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <SH color={C.muted}>{tr('lab.flag')}</SH>
                  {allFlagSteps.map((step, i) => {
                    const flagId = step.flag.id
                    const isCaptured = capturedFlags.has(flagId)
                    return (
                      <div key={i} style={{ marginBottom: 8 }}>
                        <div style={{
                          display: 'flex', gap: 4, alignItems: 'center',
                          background: 'rgba(0,0,0,0.3)',
                          border: `1px solid ${flagResults[flagId]?.correct ? C.accent : flagResults[flagId] ? C.red : 'rgba(0,255,136,0.15)'}`,
                          borderRadius: 6, padding: '3px 4px 3px 10px',
                        }}>
                          <span style={{ fontSize: 10, color: isCaptured ? C.accent : 'rgba(0,255,136,0.3)', flexShrink: 0 }}>$</span>
                          <input
                            placeholder="SF{...}"
                            value={flagInputs[flagId] || ''}
                            onChange={e => setFlagInputs(prev => ({ ...prev, [flagId]: e.target.value }))}
                            onKeyDown={e => e.key === 'Enter' && submitFlag(flagId)}
                            disabled={isCaptured}
                            style={{
                              flex: 1, border: 'none', background: 'transparent',
                              fontSize: 11, padding: '7px 4px',
                              color: isCaptured ? C.accent : C.text,
                              fontFamily: 'JetBrains Mono, monospace', outline: 'none',
                            }}
                          />
                          {allFlagSteps.length > 1 && (
                            <div style={{ fontSize: 8, fontWeight: 700, color: C.muted, letterSpacing: 1, padding: '0 8px', borderLeft: '1px solid rgba(0,255,136,0.1)', flexShrink: 0 }}>
                              FLAG {i + 1}
                            </div>
                          )}
                          <button onClick={() => submitFlag(flagId)} disabled={isCaptured} style={{
                            padding: '6px 14px', borderRadius: 5,
                            background: isCaptured ? 'rgba(0,255,136,0.1)' : 'rgba(0,255,136,0.15)',
                            color: C.accent, border: '1px solid rgba(0,255,136,0.25)',
                            fontFamily: 'inherit', fontSize: 10, fontWeight: 700,
                            cursor: isCaptured ? 'default' : 'pointer',
                            display: 'flex', alignItems: 'center', gap: 5,
                          }}>
                            <Send size={10} />
                            SUBMIT
                          </button>
                        </div>
                        {flagResults[flagId] && (
                          <div style={{
                            marginTop: 6, fontSize: 10, padding: '5px 10px', borderRadius: 5,
                            background: flagResults[flagId].correct ? 'rgba(0,255,136,0.08)' : 'rgba(255,51,102,0.08)',
                            color: flagResults[flagId].correct ? C.accent : C.red,
                            border: `1px solid ${flagResults[flagId].correct ? 'rgba(0,255,136,0.2)' : 'rgba(255,51,102,0.2)'}`,
                          }}>
                            {flagResults[flagId].correct
                              ? `✓ ${tr('lab.flagCorrect')}`
                              : `✗ ${tr('lab.flagWrong')}`}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )
            )}

            {labStatus === 'completed' && lab.attack_chain && lab.attack_chain.length > 1 && (
              <div style={{ marginBottom: 20 }}>
                <SH color={C.muted}>{tr('lab.attackChain')}</SH>
                {lab.attack_chain.map((step, i) => {
                  const phaseName = tLab(step.name, locale)
                  const objectives = step.objectives || []
                  return (
                    <div key={i} style={{
                      marginBottom: 6,
                      padding: '10px 14px',
                      borderRadius: 7,
                      background: 'rgba(0,255,136,0.02)',
                      border: '1px solid rgba(0,255,136,0.07)',
                      borderLeft: '3px solid rgba(0,255,136,0.18)',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: objectives.length ? 6 : 0 }}>
                        <span style={{
                          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                          width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                          background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.25)',
                          fontSize: 9, fontWeight: 700, color: C.muted,
                        }}>{step.phase}</span>
                        <span style={{ fontSize: 11, fontWeight: 700, color: C.textDim }}>{phaseName}</span>
                      </div>
                      {objectives.length > 0 && (
                        <ul style={{ listStyle: 'none', marginLeft: 26 }}>
                          {objectives.map((obj, j) => (
                            <li key={j} style={{ display: 'flex', gap: 6, marginBottom: 2, fontSize: 10, color: 'rgba(212,245,226,0.32)', lineHeight: 1.4 }}>
                              <span style={{ color: 'rgba(0,255,136,0.3)', flexShrink: 0 }}>›</span>
                              {tLab(obj, locale)}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )
                })}
              </div>
            )}

            {lab.attack_chain && lab.attack_chain.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <div style={{ flex: 1, height: 1, background: 'rgba(249,115,22,0.12)' }} />
                  <div style={{ fontSize: 8, fontWeight: 700, letterSpacing: 2, color: 'rgba(249,115,22,0.35)', display: 'flex', alignItems: 'center', gap: 5 }}>
                    {walkthroughRevealed ? '📖' : '🔒'} {tr('lab.walkthrough').toUpperCase()}
                  </div>
                  <div style={{ flex: 1, height: 1, background: 'rgba(249,115,22,0.12)' }} />
                </div>

                {walkthroughRevealed > 0 ? (
                  <div style={{
                    border: '1px solid rgba(249,115,22,0.25)',
                    borderRadius: 8, overflow: 'hidden',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}>
                    <div style={{
                      padding: '8px 12px', background: 'rgba(249,115,22,0.08)',
                      borderBottom: '1px solid rgba(249,115,22,0.15)',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}>
                      <span style={{ fontSize: 9, fontWeight: 700, color: 'rgba(249,115,22,0.8)', letterSpacing: 1.5 }}>
                        📖 {locale === 'ru' ? 'ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ' : 'ACTION SEQUENCE'}
                      </span>
                      <span style={{ fontSize: 8, color: 'rgba(249,115,22,0.5)' }}>
                        {lab.attack_chain.length} {locale === 'ru' ? 'шаг.' : 'steps'}
                      </span>
                    </div>
                    {lab.attack_chain.map((step, i) => {
                      const stepName = tLab(step.name, locale)
                      const deepestHint = step.hints && step.hints.length > 0 ? step.hints[step.hints.length - 1] : null
                      const hintText = deepestHint ? tLab(deepestHint.text, locale) : tLab(step.description, locale)
                      return (
                        <div key={i} style={{
                          padding: '11px 14px',
                          borderBottom: i < lab.attack_chain.length - 1 ? '1px solid rgba(249,115,22,0.08)' : 'none',
                          background: 'rgba(249,115,22,0.025)',
                        }}>
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 9, marginBottom: 5 }}>
                            <span style={{
                              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                              width: 18, height: 18, borderRadius: '50%', flexShrink: 0, marginTop: 1,
                              background: 'rgba(249,115,22,0.15)',
                              border: '1px solid rgba(249,115,22,0.3)',
                              fontSize: 9, fontWeight: 700, color: '#f97316',
                            }}>{i + 1}</span>
                            <span style={{ fontSize: 11, fontWeight: 700, color: '#f97316', lineHeight: 1.3 }}>{stepName}</span>
                          </div>
                          <div style={{ paddingLeft: 27, fontSize: 11, color: 'rgba(249,115,22,0.75)', lineHeight: 1.65 }}>
                            {hintText}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : pendingWalkthrough ? (
                  <div style={{ padding: '10px 12px', borderRadius: 6, background: 'rgba(249,115,22,0.06)', border: '1px solid rgba(249,115,22,0.3)' }}>
                    <div style={{ fontSize: 10, color: '#f97316', marginBottom: 8, lineHeight: 1.5 }}>
                      {locale === 'ru'
                        ? 'Показать полный гайд?'
                        : 'Show full walkthrough?'}
                    </div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button
                        onClick={() => { setWalkthroughRevealed(1); setPendingWalkthrough(false) }}
                        style={{ padding: '4px 12px', borderRadius: 4, cursor: 'pointer', background: 'rgba(249,115,22,0.15)', color: '#f97316', border: '1px solid rgba(249,115,22,0.4)', fontFamily: 'inherit', fontSize: 9, fontWeight: 700, letterSpacing: 1 }}
                      >
                        {tr('lab.reveal').toUpperCase()}
                      </button>
                      <button
                        onClick={() => setPendingWalkthrough(false)}
                        style={{ padding: '4px 12px', borderRadius: 4, cursor: 'pointer', background: 'transparent', color: 'rgba(255,255,255,0.3)', border: '1px solid rgba(255,255,255,0.1)', fontFamily: 'inherit', fontSize: 9, fontWeight: 700, letterSpacing: 1 }}
                      >
                        {tr('lab.cancel').toUpperCase()}
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setPendingWalkthrough(true)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6, width: '100%',
                      padding: '7px 12px', borderRadius: 5, cursor: 'pointer',
                      background: 'rgba(249,115,22,0.04)',
                      border: '1px dashed rgba(249,115,22,0.2)',
                      fontFamily: 'inherit', transition: 'all 0.15s',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'rgba(249,115,22,0.09)'; e.currentTarget.style.borderColor = 'rgba(249,115,22,0.45)' }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'rgba(249,115,22,0.04)'; e.currentTarget.style.borderColor = 'rgba(249,115,22,0.2)' }}
                  >
                    <span style={{ fontSize: 13, lineHeight: 1 }}>🔒</span>
                    <span style={{ flex: 1, textAlign: 'left', fontSize: 10, fontWeight: 700, color: 'rgba(249,115,22,0.7)', letterSpacing: 1 }}>
                      {tr('lab.stuck').toUpperCase()} — {locale === 'ru' ? 'ПОКАЗАТЬ ГАЙД' : 'SHOW WALKTHROUGH'}
                    </span>
                  </button>
                )}
              </div>
            )}

            {explanation && !isOperation && (
              <div style={{
                marginTop: 20,
                background: 'rgba(99,102,241,0.05)',
                border: '1px solid rgba(99,102,241,0.2)',
                borderLeft: '3px solid #6366f1',
                borderRadius: 8, padding: '18px 20px',
                fontFamily: 'JetBrains Mono,monospace',
              }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: '#475569', letterSpacing: 2, marginBottom: 14 }}>
                  {locale === 'ru' ? 'РАЗБОР — ПОЧЕМУ АТАКА СРАБОТАЛА' : 'DEBRIEF — WHY THIS ATTACK WORKED'}
                </div>
                <div style={{ display: 'inline-block', fontSize: 9, fontWeight: 700, letterSpacing: 1,
                  padding: '2px 8px', borderRadius: 3, background: 'rgba(99,102,241,0.15)',
                  color: '#6366f1', border: '1px solid rgba(99,102,241,0.3)', marginBottom: 12 }}>
                  {explanation.attack_vector}
                </div>
                <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.6, marginBottom: 14 }}>
                  {explanation.what_happened}
                </p>
                <div style={{ fontSize: 9, fontWeight: 700, color: '#475569', letterSpacing: 2, marginBottom: 8 }}>
                  {locale === 'ru' ? 'ПСИХОЛОГИЯ' : 'PSYCHOLOGY'}
                </div>
                <ul style={{ listStyle: 'none', marginBottom: 14 }}>
                  {explanation.psychology?.map((p, i) => (
                    <li key={i} style={{ fontSize: 11, color: '#94a3b8', marginBottom: 5, display: 'flex', gap: 8 }}>
                      <span style={{ color: '#6366f1', flexShrink: 0 }}>›</span>{p}
                    </li>
                  ))}
                </ul>
                <div style={{ fontSize: 9, fontWeight: 700, color: '#475569', letterSpacing: 2, marginBottom: 8 }}>
                  {locale === 'ru' ? 'ЗАЩИТА' : 'DEFENSE'}
                </div>
                <ul style={{ listStyle: 'none', marginBottom: 14 }}>
                  {explanation.defense?.map((d, i) => (
                    <li key={i} style={{ fontSize: 11, color: '#94a3b8', marginBottom: 5, display: 'flex', gap: 8 }}>
                      <span style={{ color: '#00ff88', flexShrink: 0 }}>›</span>{d}
                    </li>
                  ))}
                </ul>
                {explanation.real_world && (
                  <p style={{ fontSize: 10, color: '#475569', fontStyle: 'italic', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 10, marginTop: 4 }}>
                    {explanation.real_world}
                  </p>
                )}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

            <div style={{
              background: 'rgba(0,255,136,0.02)',
              border: `1px solid ${C.border}`,
              borderLeft: `3px solid rgba(0,255,136,0.35)`,
              borderRadius: 7, padding: '13px 14px',
            }}>
              <SH>{tr('lab.targetOrg')}</SH>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
                <Building size={12} color={C.accent} />
                <span style={{ fontSize: 15, fontWeight: 700, color: C.accent, textShadow: `0 0 10px ${C.accent}30` }}>
                  {lab.target_company?.name}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 9, color: C.muted, marginBottom: 3 }}>
                <Globe size={9} color={C.muted} />
                {lab.target_company?.domain}
              </div>
              {lab.target_company?.industry && (
                <div style={{ fontSize: 9, color: C.textDim, lineHeight: 1.55, marginBottom: 5 }}>
                  {lab.target_company.industry}
                </div>
              )}
              {lab.target_company?.employees?.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 9, color: C.muted }}>
                  <Users size={9} color={C.muted} />
                  {lab.target_company.employees.length} employees indexed
                </div>
              )}
            </div>

            <div style={{
              background: 'rgba(0,0,0,0.2)',
              border: `1px solid ${C.border}`,
              borderRadius: 7, padding: '13px 14px',
              transition: 'opacity 0.2s',
            }}>
              <SH>{tr('lab.attackToolkit')}</SH>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6 }}>
                <ToolBtn icon={Globe}         color={C.accent}  label={tr('lab.toolWebsite')}   href={realUrl + (companySlug ? `/${companySlug}` : '') + `?user_id=${user?.user_id || ''}`} />
                <ToolBtn icon={Phone}         color={C.orange}  label={tr('lab.toolPhone')}     href={`http://127.0.0.1:9007?user=${user.user_id}&lab=${labId}`} />
                <ToolBtn icon={Globe}         color={C.blue}    label={tr('lab.toolLinkhub')}   href="http://127.0.0.1:9003" />
                <ToolBtn icon={Mail}          color={C.purple}  label={tr('lab.toolEmail')}     href={`http://127.0.0.1:9004?user=${user.user_id}&lab_id=${labId}`} />
                <ToolBtn icon={Fish}          color={C.red}     label={tr('lab.toolPhisher')}   href={`http://127.0.0.1:9006?lab=${labId}&user=${user.user_id}`} />
                <ToolBtn icon={MessageSquare} color={C.blue}   label={tr('lab.toolMessenger')} href={`http://127.0.0.1:9003/login?lab_id=${labId}&user_id=${user.user_id}`} />
              </div>
            </div>

          </div>
        </div>
      </div>


      {labStatus === 'failed' && failureInfo && !bustDismissed && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'radial-gradient(ellipse at center, rgba(90,0,0,0.96) 0%, rgba(0,0,0,0.99) 80%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 40, textAlign: 'center', fontFamily: 'JetBrains Mono, monospace',
        }}>
          <div style={{
            position: 'absolute', inset: 0, pointerEvents: 'none',
            background: 'repeating-linear-gradient(to bottom, transparent 0, transparent 2px, rgba(255,0,0,0.04) 2px, rgba(255,0,0,0.04) 3px)',
            animation: 'scan 4s linear infinite',
          }} />
          <div style={{ fontSize: 12, letterSpacing: 5, color: '#ff9999', textTransform: 'uppercase', marginBottom: 12, zIndex: 1 }}>
            Operation Compromised
          </div>
          <h1 style={{
            fontFamily: "'Impact','Arial Black',sans-serif",
            fontSize: 118, fontWeight: 900, letterSpacing: 10,
            color: '#ff2222',
            textShadow: '0 0 30px rgba(255,40,40,0.9), 0 0 60px rgba(255,0,0,0.5), 3px 3px 0 #000',
            margin: 0, lineHeight: 1, zIndex: 1,
            animation: 'gtaBust 1.2s ease-out',
          }}>HACKER</h1>
          <h1 style={{
            fontFamily: "'Impact','Arial Black',sans-serif",
            fontSize: 118, fontWeight: 900, letterSpacing: 10,
            color: '#ff2222',
            textShadow: '0 0 30px rgba(255,40,40,0.9), 0 0 60px rgba(255,0,0,0.5), 3px 3px 0 #000',
            margin: '-16px 0 0 0', lineHeight: 1, zIndex: 1,
            animation: 'gtaBust 1.2s ease-out',
          }}>EXPOSED</h1>
          <h2 style={{
            fontFamily: "'Impact','Arial Black',sans-serif",
            fontSize: 32, letterSpacing: 5, color: '#ff7070', margin: '24px 0 12px',
            textShadow: '0 0 12px rgba(255,50,50,0.6)', zIndex: 1,
          }}>// MISSION FAILED //</h2>
          {failureInfo.persona && (
            <div style={{ fontSize: 13, color: '#ff9999', fontStyle: 'italic', marginBottom: 12, zIndex: 1 }}>
              {locale === 'ru' ? 'Раскрыты:' : 'Detected by:'} {failureInfo.persona}
            </div>
          )}
          {failureInfo.reason && (
            <div style={{
              fontSize: 13, color: '#ffd7d7', lineHeight: 1.65, maxWidth: 600,
              padding: '13px 20px', background: 'rgba(255,0,0,0.08)',
              border: '1px solid rgba(255,80,80,0.2)', borderRadius: 10, marginBottom: 24, zIndex: 1,
            }}>
              {failureInfo.reason}
            </div>
          )}
          <div style={{ display: 'flex', gap: 12, zIndex: 1 }}>
            <button
              onClick={async () => {
                await api.resetLab(labId, user.user_id).catch(() => {})
                await refreshStatus()
              }}
              style={{
                padding: '12px 24px', fontSize: 13, borderRadius: 8,
                background: '#ef4444', color: '#fff',
                border: 'none', cursor: 'pointer', fontWeight: 700,
                fontFamily: 'JetBrains Mono, monospace',
                boxShadow: '0 0 20px rgba(239,68,68,0.4)',
              }}
            >
              {locale === 'ru' ? '↺ ПОПРОБОВАТЬ СНОВА' : '↺ TRY AGAIN'}
            </button>
            <button onClick={() => navigate('/labs')} style={{
              padding: '12px 24px', fontSize: 13, borderRadius: 8,
              background: 'rgba(255,255,255,0.08)', color: '#fff',
              border: '1px solid #555', cursor: 'pointer',
              fontFamily: 'JetBrains Mono, monospace',
            }}>
              {locale === 'ru' ? 'К списку лаб' : 'Back to Labs'}
            </button>
            <button onClick={() => setBustDismissed(true)} style={{
              padding: '12px 24px', fontSize: 13, borderRadius: 8,
              background: 'transparent', color: '#ff9999',
              border: '1px solid rgba(255,100,100,0.3)', cursor: 'pointer',
              fontFamily: 'JetBrains Mono, monospace',
            }}>
              {locale === 'ru' ? '✕ ЗАКРЫТЬ' : '✕ DISMISS'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
