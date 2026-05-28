import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useApp } from '../store'

const TEMPLATES = {
  microsoft365: { label: 'Microsoft 365', color: '#0078d4', field: 'Email or phone' },
  google:       { label: 'Google',         color: '#4285f4', field: 'Email or phone' },
  slack:        { label: 'Slack',          color: '#611f69', field: 'Email address'  },
  generic_bank: { label: 'Generic Bank',   color: '#1a3a5c', field: 'Username'       },
  generic:      { label: 'Generic Login',  color: '#374151', field: 'Username'       },
}

const C = {
  bg:          '#060a0f',
  surface:     '#0a0e17',
  accent:      '#00ff88',
  accentDim:   'rgba(0,255,136,0.08)',
  accentBorder:'rgba(0,255,136,0.22)',
  red:         '#ef4444',
  redDim:      'rgba(239,68,68,0.08)',
  orange:      '#f59e0b',
  blue:        '#3b82f6',
  purple:      '#6366f1',
  gold:        '#fbbf24',
  text:        '#e2e8f0',
  sub:         '#94a3b8',
  muted:       '#475569',
  border:      'rgba(255,255,255,0.06)',
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

const SSL_OPTIONS = [
  { value: 'valid',           label: '🔒 Valid HTTPS',         desc: 'Trusted cert, green padlock',          points: 20 },
  { value: 'self_signed',     label: '⚠️ Self-Signed',          desc: 'Untrusted cert, browser warning',       points: 5  },
  { value: 'expired',         label: '⚠️ Expired Cert',         desc: 'Cert expired, browser warning',         points: 5  },
  { value: 'domain_mismatch', label: '⚠️ Domain Mismatch',      desc: 'Cert issued for different domain',      points: 3  },
  { value: 'none',            label: '🔓 No HTTPS (HTTP)',      desc: 'No padlock, browser shows Not Secure',  points: 0  },
]

function calcScore(domain, company, sslType) {
  let score = 15
  const d = domain.toLowerCase()
  if (d && /microsoft|google|secure|login|account|portal/.test(d)) score += 25
  if (d && (d.match(/\./g) || []).length >= 2) score += 15
  if (d) score += 10
  if (company.trim()) score += 10
  const sslOpt = SSL_OPTIONS.find(o => o.value === sslType)
  score += sslOpt ? sslOpt.points : 0
  return Math.min(score, 95)
}

function scoreColor(score) {
  if (score >= 70) return C.accent
  if (score >= 40) return C.orange
  return C.red
}

export default function Phisher() {
  const { user } = useApp()
  const [searchParams] = useSearchParams()
  const labId = searchParams.get('lab') || ''

  const [template,   setTemplate]   = useState('microsoft365')
  const [domain,     setDomain]     = useState('')
  const [company,    setCompany]    = useState('')
  const [sslType,    setSslType]    = useState('valid')
  const [generating, setGenerating] = useState(false)
  const [lastUrl,    setLastUrl]    = useState('')
  const [sites,      setSites]      = useState([])
  const [copied,     setCopied]     = useState(false)
  const [error,      setError]      = useState('')
  const [focusDomain,  setFocusDomain]  = useState(false)
  const [focusCompany, setFocusCompany] = useState(false)

  const userId = user?.user_id || 1

  const loadSites = useCallback(async () => {
    try {
      const res = await fetch(`/api/phish/sites?lab_id=${encodeURIComponent(labId)}&user_id=${userId}`)
      if (!res.ok) return
      const data = await res.json()
      setSites(data.sites || [])
    } catch {}
  }, [labId, userId])

  useEffect(() => {
    loadSites()
    const iv = setInterval(loadSites, 8000)
    return () => clearInterval(iv)
  }, [loadSites])

  async function createPage() {
    setGenerating(true)
    setError('')
    try {
      const res = await fetch('/api/phish/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lab_id: labId,
          user_id: userId,
          template,
          domain: domain.trim() || 'secure-login.example.com',
          company_name: company.trim(),
          ssl_type: sslType,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(`Error ${res.status}: ${data.detail || JSON.stringify(data)}`)
        return
      }
      setLastUrl(`http://127.0.0.1:8000/p/${data.site_id}`)
      await loadSites()
    } catch (e) {
      setError(`Network error: ${e.message}`)
    } finally {
      setGenerating(false)
    }
  }

  function copyUrl() {
    if (!lastUrl) return
    navigator.clipboard.writeText(lastUrl).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
  }

  const tpl   = TEMPLATES[template]
  const score = calcScore(domain, company, sslType)
  const sColor = scoreColor(score)
  const domainTrimmed = domain.trim()

  const hasBrand    = domainTrimmed && /microsoft|google|secure|login|account|portal/.test(domainTrimmed.toLowerCase())
  const hasSubdomain = domainTrimmed && (domainTrimmed.match(/\./g) || []).length >= 2
  const hasDomain   = !!domainTrimmed
  const hasCompany  = !!company.trim()

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
              PHISHING STUDIO // SITE FACTORY
            </div>
            <div style={{ fontSize: 9, color: C.muted, marginTop: 3, letterSpacing: 1 }}>
              {labId ? `LAB ${labId.toUpperCase()}` : 'NO LAB SELECTED'} · UID {userId}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              display: 'inline-block', width: 6, height: 6, borderRadius: '50%',
              background: C.accent, boxShadow: `0 0 6px ${C.accent}`,
            }} />
            <span style={{ fontSize: 9, color: C.muted, letterSpacing: 1 }}>OPERATOR</span>
          </div>
        </div>

        {/* MAIN 2-COLUMN GRID */}
        <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 16, alignItems: 'start' }}>

          {/* LEFT COLUMN */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

            {/* TEMPLATES */}
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: '14px 12px',
            }}>
              <SH>Templates</SH>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {Object.entries(TEMPLATES).map(([k, v]) => (
                  <div
                    key={k}
                    onClick={() => setTemplate(k)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      padding: '7px 10px', borderRadius: 4, cursor: 'pointer',
                      background: template === k ? C.accentDim : 'transparent',
                      border: `1px solid ${template === k ? C.accentBorder : 'transparent'}`,
                      color: template === k ? C.accent : C.sub,
                      fontSize: 11, fontFamily: 'JetBrains Mono, monospace',
                      transition: 'all 0.1s',
                    }}
                  >
                    <span style={{ fontSize: 11, color: template === k ? C.accent : C.muted }}>
                      {template === k ? '●' : '○'}
                    </span>
                    {v.label}
                  </div>
                ))}
              </div>
            </div>

            {/* QUALITY SCORE */}
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: '14px 12px',
            }}>
              <SH>Quality Score</SH>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 7 }}>
                <span style={{ fontSize: 18, fontWeight: 700, color: sColor, fontFamily: 'JetBrains Mono, monospace' }}>
                  {score}%
                </span>
                <span style={{ fontSize: 8, color: sColor, letterSpacing: 1 }}>
                  {score >= 70 ? 'GOOD' : score >= 40 ? 'FAIR' : 'WEAK'}
                </span>
              </div>

              <div style={{
                height: 4, background: 'rgba(255,255,255,0.05)',
                borderRadius: 2, overflow: 'hidden', marginBottom: 12,
              }}>
                <div style={{
                  height: '100%', width: `${score}%`,
                  background: sColor, borderRadius: 2,
                  transition: 'width 0.4s ease, background 0.3s',
                  boxShadow: score >= 70 ? `0 0 6px ${sColor}66` : 'none',
                }} />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                {[
                  { pass: hasBrand,             label: 'Domain spoofed' },
                  { pass: hasSubdomain,          label: 'Subdomain chain' },
                  { pass: hasDomain,             label: 'Domain set' },
                  { pass: hasCompany,            label: 'Company set' },
                  { pass: sslType === 'valid',   label: 'Valid SSL cert' },
                ].map((item, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 10 }}>
                    <span style={{ color: item.pass ? C.accent : C.red, fontSize: 10 }}>
                      {item.pass ? '✓' : '✗'}
                    </span>
                    <span style={{ color: item.pass ? C.sub : C.muted }}>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* RIGHT COLUMN */}
          <div style={{
            background: C.surface, border: `1px solid ${C.border}`,
            borderRadius: 8, padding: '16px 18px',
            display: 'flex', flexDirection: 'column', gap: 16,
          }}>

            <SH>Configuration</SH>

            {/* INPUTS */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div>
                <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginBottom: 5, fontFamily: 'JetBrains Mono, monospace' }}>
                  FAKE DOMAIN
                </div>
                <input
                  value={domain}
                  onChange={e => setDomain(e.target.value)}
                  onFocus={() => setFocusDomain(true)}
                  onBlur={() => setFocusDomain(false)}
                  placeholder="e.g. microsoft-secure.login.com"
                  maxLength={80}
                  style={{
                    width: '100%',
                    background: 'rgba(255,255,255,0.03)',
                    border: `1px solid ${focusDomain ? 'rgba(0,255,136,0.35)' : C.border}`,
                    borderRadius: 6, padding: '8px 11px',
                    color: C.text, fontSize: 12,
                    fontFamily: 'JetBrains Mono, monospace',
                    outline: 'none', boxSizing: 'border-box',
                    transition: 'border-color 0.15s',
                  }}
                />
              </div>

              <div>
                <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginBottom: 5, fontFamily: 'JetBrains Mono, monospace' }}>
                  COMPANY NAME
                </div>
                <input
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  onFocus={() => setFocusCompany(true)}
                  onBlur={() => setFocusCompany(false)}
                  placeholder="Leave blank to use template default"
                  maxLength={60}
                  style={{
                    width: '100%',
                    background: 'rgba(255,255,255,0.03)',
                    border: `1px solid ${focusCompany ? 'rgba(0,255,136,0.35)' : C.border}`,
                    borderRadius: 6, padding: '8px 11px',
                    color: C.text, fontSize: 12,
                    fontFamily: 'JetBrains Mono, monospace',
                    outline: 'none', boxSizing: 'border-box',
                    transition: 'border-color 0.15s',
                  }}
                />
              </div>
            </div>

            {/* SSL CERTIFICATE */}
            <div>
              <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginBottom: 8, fontFamily: 'JetBrains Mono, monospace' }}>
                SSL CERTIFICATE
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {SSL_OPTIONS.map(opt => (
                  <div
                    key={opt.value}
                    onClick={() => setSslType(opt.value)}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '7px 10px', borderRadius: 5, cursor: 'pointer',
                      background: sslType === opt.value ? C.accentDim : 'transparent',
                      border: `1px solid ${sslType === opt.value ? C.accentBorder : C.border}`,
                      transition: 'all 0.1s',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 10, color: sslType === opt.value ? C.accent : C.muted }}>
                        {sslType === opt.value ? '●' : '○'}
                      </span>
                      <div>
                        <div style={{ fontSize: 11, color: sslType === opt.value ? C.accent : C.sub, fontFamily: 'JetBrains Mono, monospace' }}>
                          {opt.label}
                        </div>
                        <div style={{ fontSize: 9, color: C.muted, fontFamily: 'JetBrains Mono, monospace' }}>
                          {opt.desc}
                        </div>
                      </div>
                    </div>
                    <span style={{ fontSize: 9, color: opt.points > 0 ? C.accent : C.red, fontFamily: 'JetBrains Mono, monospace' }}>
                      +{opt.points}pts
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* PREVIEW */}
            <div>
              <SH>Preview</SH>
              <div style={{
                background: 'rgba(255,255,255,0.02)',
                border: `1px solid ${C.border}`,
                borderRadius: 6, padding: '12px 14px',
              }}>
                <div style={{ fontSize: 9, color: C.muted, marginBottom: 8, letterSpacing: 0.5 }}>
                  {SSL_OPTIONS.find(o => o.value === sslType)?.label.split(' ')[0]}{' '}
                  {sslType === 'none' ? 'http://' : 'https://'}{domainTrimmed || 'example-secure.com'}
                </div>
                <div style={{ fontSize: 12, fontWeight: 700, color: C.text, marginBottom: 6 }}>
                  {company.trim() || tpl.label}
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <div style={{
                    flex: 1, background: 'rgba(255,255,255,0.04)', border: `1px solid ${C.border}`,
                    borderRadius: 4, padding: '5px 8px', fontSize: 10, color: C.muted,
                  }}>
                    {tpl.field}
                  </div>
                  <div style={{
                    flex: 1, background: 'rgba(255,255,255,0.04)', border: `1px solid ${C.border}`,
                    borderRadius: 4, padding: '5px 8px', fontSize: 10, color: C.muted,
                  }}>
                    Password
                  </div>
                </div>
              </div>
            </div>

            {/* ERROR */}
            {error && (
              <div style={{
                background: C.redDim, border: `1px solid rgba(239,68,68,0.25)`,
                borderRadius: 6, padding: '8px 12px',
                fontSize: 10, color: C.red, fontFamily: 'JetBrains Mono, monospace',
              }}>
                [ERR] {error}
              </div>
            )}

            {/* DEPLOY BUTTON */}
            <button
              onClick={createPage}
              disabled={generating}
              style={{
                width: '100%', padding: '11px 0', borderRadius: 7,
                background: 'rgba(0,255,136,0.1)', color: C.accent,
                border: '1px solid rgba(0,255,136,0.3)',
                fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 700, fontSize: 12, letterSpacing: 2,
                cursor: generating ? 'default' : 'pointer',
                opacity: generating ? 0.6 : 1,
                transition: 'opacity 0.15s',
              }}
            >
              {generating ? '// GENERATING...' : '⚡ DEPLOY PHISHING PAGE'}
            </button>

            {/* SUCCESS URL */}
            {lastUrl && (
              <div style={{
                background: C.accentDim, border: `1px solid ${C.accentBorder}`,
                borderRadius: 6, padding: '8px 12px',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <span style={{ fontSize: 9, color: C.muted, flexShrink: 0, fontFamily: 'JetBrains Mono, monospace' }}>URL</span>
                <span
                  style={{
                    fontSize: 11, color: C.accent, fontFamily: 'JetBrains Mono, monospace',
                    flex: 1, cursor: 'pointer',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}
                  onClick={copyUrl}
                >
                  {copied ? '// COPIED TO CLIPBOARD' : lastUrl}
                </span>
              </div>
            )}

          </div>
        </div>

        {/* ACTIVE PAGES SECTION */}
        <div style={{ marginTop: 20 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12,
            paddingBottom: 10, borderBottom: `1px solid ${C.border}`,
          }}>
            <div style={{ fontSize: 8, fontWeight: 700, color: C.muted, letterSpacing: 2, fontFamily: 'JetBrains Mono, monospace' }}>
              ACTIVE PAGES
            </div>
            <div style={{
              fontSize: 9, color: sites.length ? C.accent : C.muted,
              background: sites.length ? C.accentDim : 'transparent',
              border: `1px solid ${sites.length ? C.accentBorder : 'transparent'}`,
              borderRadius: 3, padding: '1px 7px', fontFamily: 'JetBrains Mono, monospace',
            }}>
              {sites.length}
            </div>
          </div>

          {sites.length === 0 ? (
            <div style={{
              textAlign: 'center', color: C.muted, fontSize: 11,
              padding: '32px 0', fontFamily: 'JetBrains Mono, monospace',
              border: `1px dashed rgba(255,255,255,0.05)`, borderRadius: 8,
            }}>
              // NO PAGES DEPLOYED
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: 10,
            }}>
              {sites.map(s => {
                const t = TEMPLATES[s.template] || TEMPLATES.generic
                const url = `http://127.0.0.1:8000/p/${s.site_id}`
                const timeStr = s.created_at
                  ? new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  : '--:--'
                return (
                  <div
                    key={s.site_id}
                    style={{
                      background: 'rgba(255,255,255,0.02)', border: `1px solid ${C.border}`,
                      borderLeft: `3px solid ${s.harvest_count ? C.accent : C.muted}`,
                      borderRadius: 6, padding: '10px 12px',
                    }}
                  >
                    <div style={{
                      fontSize: 11, fontWeight: 700, color: C.text,
                      fontFamily: 'JetBrains Mono, monospace', marginBottom: 4,
                    }}>
                      {s.domain || 'unknown'}
                    </div>
                    <div style={{ fontSize: 9, color: C.muted, marginBottom: 6, fontFamily: 'JetBrains Mono, monospace' }}>
                      {t.label} · {timeStr}
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: 10, color: s.harvest_count ? C.accent : C.muted, fontFamily: 'JetBrains Mono, monospace' }}>
                        {s.harvest_count ? `${s.harvest_count} CREDS` : '0 HITS'}
                      </span>
                      <span
                        style={{ fontSize: 9, color: C.muted, fontFamily: 'JetBrains Mono, monospace', cursor: 'pointer' }}
                        onClick={() => copyToClipboard(url)}
                      >
                        COPY URL
                      </span>
                    </div>
                    {(s.harvests || []).map((h, i) => (
                      <div
                        key={i}
                        style={{
                          marginTop: 4, background: 'rgba(0,255,136,0.04)',
                          borderRadius: 4, padding: '4px 8px', fontSize: 10,
                          fontFamily: 'JetBrains Mono, monospace', display: 'flex', gap: 10,
                        }}
                      >
                        <span style={{ color: C.gold, minWidth: 80 }}>{h.persona_name}</span>
                        <span style={{ color: C.text }}>{h.username} / {h.password}</span>
                      </div>
                    ))}
                  </div>
                )
              })}
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
