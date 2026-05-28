import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useApp } from '../store'

const LINKHUB = 'http://127.0.0.1:9003'

const C = {
  bg:           '#060a0f',
  surface:      '#0a0e17',
  accent:       '#00ff88',
  accentDim:    'rgba(0,255,136,0.08)',
  accentBorder: 'rgba(0,255,136,0.22)',
  red:          '#ef4444',
  redDim:       'rgba(239,68,68,0.08)',
  orange:       '#f59e0b',
  blue:         '#3b82f6',
  text:         '#e2e8f0',
  sub:          '#94a3b8',
  muted:        '#475569',
  border:       'rgba(255,255,255,0.06)',
}

function SH({ children }) {
  return (
    <div style={{
      fontSize: 8, fontWeight: 700, color: C.muted,
      letterSpacing: 2, marginBottom: 10, textTransform: 'uppercase',
      fontFamily: 'JetBrains Mono, monospace',
    }}>
      {children}
    </div>
  )
}

function NpcRow({ account, selected, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 10px', borderRadius: 4, cursor: 'pointer',
        background: selected ? C.accentDim : 'transparent',
        border: `1px solid ${selected ? C.accentBorder : 'transparent'}`,
        color: selected ? C.accent : C.sub,
        fontSize: 11, fontFamily: 'JetBrains Mono, monospace',
        transition: 'all 0.1s',
        marginBottom: 2,
      }}
    >
      <span style={{ fontSize: 11, color: selected ? C.accent : C.muted }}>
        {selected ? '●' : '○'}
      </span>
      <div>
        <div style={{ fontSize: 11, color: selected ? C.accent : C.sub }}>{account.name}</div>
        <div style={{ fontSize: 9, color: C.muted }}>{account.email}</div>
      </div>
    </div>
  )
}

function MessageCard({ msg, expanded, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: C.surface, border: `1px solid ${C.border}`,
        borderRadius: 6, padding: '12px 14px', cursor: 'pointer',
        marginBottom: 8,
        transition: 'border-color 0.15s',
      }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(0,255,136,0.2)' }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = C.border }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
        <div>
          <span style={{ fontSize: 11, fontWeight: 700, color: C.accent, fontFamily: 'JetBrains Mono, monospace' }}>
            {msg.from}
          </span>
          <span style={{ fontSize: 10, color: C.muted, marginLeft: 8, fontFamily: 'JetBrains Mono, monospace' }}>
            &lt;{msg.from_email}&gt;
          </span>
        </div>
        <span style={{ fontSize: 9, color: C.muted, fontFamily: 'JetBrains Mono, monospace', whiteSpace: 'nowrap' }}>
          {msg.date}
        </span>
      </div>
      <div style={{ fontSize: 11, fontWeight: 600, color: C.text, fontFamily: 'JetBrains Mono, monospace', marginBottom: 4 }}>
        {msg.subject}
      </div>
      {expanded && (
        <div style={{
          marginTop: 10, paddingTop: 10, borderTop: `1px solid ${C.border}`,
          fontSize: 11, color: C.sub, lineHeight: 1.75,
          fontFamily: 'JetBrains Mono, monospace', whiteSpace: 'pre-wrap',
        }}>
          {msg.body}
        </div>
      )}
      {!expanded && (
        <div style={{ fontSize: 10, color: C.muted, fontFamily: 'JetBrains Mono, monospace' }}>
          {msg.body.slice(0, 80)}…
        </div>
      )}
    </div>
  )
}

export default function Messenger() {
  const { user } = useApp()
  const [searchParams] = useSearchParams()
  const labId = searchParams.get('lab') || ''

  const [accounts,    setAccounts]    = useState([])
  const [selectedAcc, setSelectedAcc] = useState(null)

  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [loading,  setLoading]  = useState(false)
  const [loginErr, setLoginErr] = useState('')

  const [session,   setSession]   = useState(null)
  const [messages,  setMessages]  = useState([])
  const [expanded,  setExpanded]  = useState(null)
  const [fetching,  setFetching]  = useState(false)

  const userId = user?.user_id || 1

  useEffect(() => {
    async function loadHints() {
      try {
        const url = labId
          ? `${LINKHUB}/api/npc-credentials-hint?lab_id=${encodeURIComponent(labId)}`
          : `${LINKHUB}/api/npc-credentials-hint`
        const res = await fetch(url)
        if (!res.ok) return
        const data = await res.json()
        setAccounts(data.accounts || [])
      } catch {}
    }
    loadHints()
  }, [labId])

  function selectAccount(acc) {
    setSelectedAcc(acc)
    setEmail(acc.email)
    setPassword('')
    setLoginErr('')
    setSession(null)
    setMessages([])
    setExpanded(null)
  }

  async function doLogin() {
    if (!email.trim() || !password.trim()) {
      setLoginErr('Enter email and password')
      return
    }
    setLoading(true)
    setLoginErr('')
    try {
      const res = await fetch(`${LINKHUB}/api/npc-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password: password.trim() }),
      })
      const data = await res.json()
      if (data.success) {
        setSession(data)
        loadInbox(data.slug)
      } else {
        setLoginErr(data.error || 'Authentication failed')
      }
    } catch (e) {
      setLoginErr(`Connection error: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  async function loadInbox(slug) {
    setFetching(true)
    try {
      const res = await fetch(`${LINKHUB}/api/npc-inbox/${slug}`)
      const data = await res.json()
      setMessages(data.messages || [])
    } catch {}
    setFetching(false)
  }

  function logout() {
    setSession(null)
    setMessages([])
    setPassword('')
    setLoginErr('')
    setExpanded(null)
  }

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      background: C.bg,
      color: C.text,
      fontFamily: 'JetBrains Mono, monospace',
      padding: '22px 24px',
    }}>
      <div style={{ maxWidth: 1040, margin: '0 auto' }}>

        {/* HEADER */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: 20, paddingBottom: 14,
          borderBottom: `1px solid ${C.border}`,
        }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.accent, letterSpacing: 1.5 }}>
              MESSENGER // NPC ACCOUNT ACCESS
            </div>
            <div style={{ fontSize: 9, color: C.muted, marginTop: 3, letterSpacing: 1 }}>
              {labId ? `LAB ${labId.toUpperCase()}` : 'ALL LABS'} · UID {userId}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              display: 'inline-block', width: 6, height: 6, borderRadius: '50%',
              background: session ? C.accent : C.muted,
              boxShadow: session ? `0 0 6px ${C.accent}` : 'none',
            }} />
            <span style={{ fontSize: 9, color: C.muted, letterSpacing: 1 }}>
              {session ? `LOGGED IN: ${session.name.toUpperCase()}` : 'NOT AUTHENTICATED'}
            </span>
          </div>
        </div>

        {/* MAIN GRID */}
        <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 16, alignItems: 'start' }}>

          {/* LEFT COLUMN — NPC ACCOUNTS */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: '14px 12px',
            }}>
              <SH>NPC Accounts</SH>
              {accounts.length === 0 ? (
                <div style={{ fontSize: 10, color: C.muted }}>No accounts discovered yet.<br />Phish targets first.</div>
              ) : (
                <div>
                  {accounts.map(acc => (
                    <NpcRow
                      key={acc.email}
                      account={acc}
                      selected={selectedAcc?.email === acc.email}
                      onClick={() => selectAccount(acc)}
                    />
                  ))}
                </div>
              )}
            </div>

            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: '14px 12px',
            }}>
              <SH>How To Use</SH>
              <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.7 }}>
                <div style={{ marginBottom: 6 }}>
                  <span style={{ color: C.accent }}>1.</span> Phish NPC credentials via Email Client or Phone Terminal
                </div>
                <div style={{ marginBottom: 6 }}>
                  <span style={{ color: C.accent }}>2.</span> Select account from list or enter email manually
                </div>
                <div>
                  <span style={{ color: C.accent }}>3.</span> Read inbox — find intel, flag hints, internal comms
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN */}
          <div style={{
            background: C.surface, border: `1px solid ${C.border}`,
            borderRadius: 8, padding: '16px 18px',
          }}>

            {!session ? (
              /* LOGIN FORM */
              <div>
                <SH>Authentication</SH>
                <div style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginBottom: 5 }}>
                    NPC EMAIL
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') doLogin() }}
                    placeholder="target@company.com"
                    style={{
                      width: '100%', boxSizing: 'border-box',
                      background: 'rgba(0,0,0,0.4)',
                      border: `1px solid rgba(0,255,136,0.12)`,
                      borderRadius: 5, padding: '10px 12px',
                      fontSize: 12, color: C.text,
                      fontFamily: 'JetBrains Mono, monospace', outline: 'none',
                    }}
                  />
                </div>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginBottom: 5 }}>
                    PASSWORD (HARVESTED)
                  </div>
                  <input
                    type="text"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') doLogin() }}
                    placeholder="harvested credential..."
                    style={{
                      width: '100%', boxSizing: 'border-box',
                      background: 'rgba(0,0,0,0.4)',
                      border: `1px solid rgba(0,255,136,0.12)`,
                      borderRadius: 5, padding: '10px 12px',
                      fontSize: 12, color: C.text,
                      fontFamily: 'JetBrains Mono, monospace', outline: 'none',
                      letterSpacing: 1,
                    }}
                  />
                </div>

                {loginErr && (
                  <div style={{
                    fontSize: 10, color: C.red, marginBottom: 12,
                    background: C.redDim, border: `1px solid rgba(239,68,68,0.2)`,
                    borderRadius: 4, padding: '8px 10px',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}>
                    ✗ {loginErr}
                  </div>
                )}

                <button
                  onClick={doLogin}
                  disabled={loading}
                  style={{
                    width: '100%', padding: '11px',
                    background: loading ? 'transparent' : C.accentDim,
                    border: `1px solid ${C.accentBorder}`,
                    borderRadius: 5,
                    fontSize: 11, fontWeight: 700, letterSpacing: 1,
                    color: loading ? C.muted : C.accent,
                    cursor: loading ? 'wait' : 'pointer',
                    fontFamily: 'JetBrains Mono, monospace',
                    transition: 'all 0.15s',
                  }}
                >
                  {loading ? 'AUTHENTICATING...' : 'ACCESS ACCOUNT →'}
                </button>

                <div style={{
                  marginTop: 20, padding: '12px 14px',
                  background: 'rgba(245,158,11,0.05)',
                  border: '1px solid rgba(245,158,11,0.15)',
                  borderRadius: 5,
                }}>
                  <div style={{ fontSize: 9, color: C.orange, letterSpacing: 2, marginBottom: 6, fontWeight: 700 }}>
                    OPERATOR HINT
                  </div>
                  <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.65 }}>
                    Credentials are obtained by deploying phishing pages (Phisher tool) or calling targets via Phone Terminal. The NPC must &ldquo;fall&rdquo; for the attack before their inbox is accessible.
                  </div>
                </div>
              </div>
            ) : (
              /* INBOX VIEW */
              <div>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginBottom: 16, paddingBottom: 12,
                  borderBottom: `1px solid ${C.border}`,
                }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: C.accent }}>
                      INBOX — {session.name.toUpperCase()}
                    </div>
                    <div style={{ fontSize: 9, color: C.muted, marginTop: 2 }}>
                      {session.slug} · {session.lab_id}
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    style={{
                      fontSize: 9, fontWeight: 700, letterSpacing: 1,
                      padding: '5px 10px', borderRadius: 4,
                      background: 'transparent',
                      border: '1px solid rgba(255,51,102,0.2)',
                      color: 'rgba(255,51,102,0.6)',
                      cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace',
                    }}
                  >
                    LOG OUT
                  </button>
                </div>

                {fetching ? (
                  <div style={{ fontSize: 11, color: C.muted, padding: '20px 0', textAlign: 'center' }}>
                    loading messages...
                  </div>
                ) : messages.length === 0 ? (
                  <div style={{
                    fontSize: 11, color: C.muted, padding: '30px 20px', textAlign: 'center',
                    border: `1px dashed ${C.border}`, borderRadius: 6,
                  }}>
                    No messages in this inbox.
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: 9, color: C.muted, letterSpacing: 2, marginBottom: 12, fontWeight: 700 }}>
                      {messages.length} MESSAGE{messages.length !== 1 ? 'S' : ''} — CLICK TO EXPAND
                    </div>
                    {messages.map((msg, i) => (
                      <MessageCard
                        key={i}
                        msg={msg}
                        expanded={expanded === i}
                        onClick={() => setExpanded(expanded === i ? null : i)}
                      />
                    ))}
                  </div>
                )}

                <div style={{
                  marginTop: 16, padding: '10px 12px',
                  background: C.accentDim,
                  border: `1px solid ${C.accentBorder}`,
                  borderRadius: 5,
                }}>
                  <div style={{ fontSize: 9, color: C.accent, letterSpacing: 2, marginBottom: 4, fontWeight: 700 }}>
                    INTEL NOTE
                  </div>
                  <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.65 }}>
                    Internal emails may contain access codes, credentials, or flag components. Record anything useful before logging out.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
