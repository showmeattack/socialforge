import { useState, useEffect } from 'react'
import { useApp } from '../store'
import { t } from '../i18n'
import { api } from '../api'
import { Key, Cpu, Globe, Check, Terminal } from 'lucide-react'

const C = {
  bg:       '#060a0f',
  surface:  '#0b1014',
  accent:   '#00ff88',
  muted:    'rgba(0,255,136,0.38)',
  text:     '#d4f5e2',
  textDim:  'rgba(212,245,226,0.5)',
  border:   'rgba(0,255,136,0.1)',
  borderHot:'rgba(0,255,136,0.28)',
}

function Card({ icon: Icon, label, children }) {
  const [hov, setHov] = useState(false)
  return (
    <div
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: 'rgba(0,255,136,0.02)',
        border: `1px solid ${hov ? C.borderHot : C.border}`,
        borderRadius: 8,
        padding: '18px 20px',
        marginBottom: 14,
        transition: 'border-color 0.15s',
      }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16,
      }}>
        <Icon size={14} color={C.accent} />
        <span style={{
          fontSize: 10, fontWeight: 700, color: C.muted,
          letterSpacing: 2, textTransform: 'uppercase',
        }}>
          {label}
        </span>
      </div>
      {children}
    </div>
  )
}

const inputStyle = {
  width: '100%',
  background: '#040809',
  border: '1px solid rgba(0,255,136,0.15)',
  color: C.accent,
  fontFamily: 'JetBrains Mono, monospace',
  borderRadius: 6,
  padding: '8px 12px',
  fontSize: 12,
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.15s',
}

export default function Settings() {
  const { locale, setLocale } = useApp()
  const tr = (key) => t(key, locale)

  const [apiKey, setApiKey]   = useState('')
  const [model, setModel]     = useState('')
  const [models, setModels]   = useState([])
  const [saved, setSaved]     = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getSettings().then(d => {
      setApiKey(d.openrouter_api_key_masked || '')
      setModel(d.openrouter_model)
      setModels(d.available_models || [])
    }).catch(() => {})
  }, [])

  const save = async () => {
    setLoading(true)
    setSaved(false)
    try {
      const payload = {}
      if (apiKey && !apiKey.includes('***') && !apiKey.includes('...')) {
        payload.openrouter_api_key = apiKey
      }
      payload.openrouter_model = model
      await api.updateSettings(payload)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      background: C.bg,
      fontFamily: 'JetBrains Mono, monospace',
      padding: '40px 24px',
    }}>
      <div style={{ maxWidth: 560, margin: '0 auto' }}>

        <div style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: 9, color: C.muted, letterSpacing: 3, fontWeight: 700 }}>
              SOCIALFORGE // CONFIGURATION
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Terminal size={18} color={C.accent} style={{ filter: 'drop-shadow(0 0 5px rgba(0,255,136,0.4))' }} />
            <h1 style={{
              fontSize: 22, fontWeight: 700, color: C.text,
              letterSpacing: 0.5, margin: 0,
            }}>
              <span style={{ color: C.accent }}>{'> '}</span>
              {tr('settings.title').toUpperCase()}
            </h1>
          </div>
        </div>

        <Card icon={Key} label={tr('settings.apiKey')}>
          <input
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder={tr('settings.apiKeyPlaceholder')}
            style={inputStyle}
            onFocus={e => { e.target.style.borderColor = 'rgba(0,255,136,0.4)' }}
            onBlur={e => { e.target.style.borderColor = 'rgba(0,255,136,0.15)' }}
          />
          <p style={{ fontSize: 10, color: C.textDim, marginTop: 8, marginBottom: 0 }}>
            {locale === 'ru' ? 'Ключ на ' : 'Get key at '}
            <a
              href="https://openrouter.ai/keys"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: C.accent, textDecoration: 'none' }}
            >
              openrouter.ai/keys
            </a>
          </p>
        </Card>

        <Card icon={Cpu} label={tr('settings.model')}>
          <select
            value={model}
            onChange={e => setModel(e.target.value)}
            style={{
              ...inputStyle,
              color: C.text,
              cursor: 'pointer',
            }}
            onFocus={e => { e.target.style.borderColor = 'rgba(0,255,136,0.4)' }}
            onBlur={e => { e.target.style.borderColor = 'rgba(0,255,136,0.15)' }}
          >
            {models.map(m => (
              <option key={m.id} value={m.id} style={{ background: '#040809', color: C.text }}>
                {m.name} ({m.id})
              </option>
            ))}
          </select>
        </Card>

        <Card icon={Globe} label={tr('settings.language')}>
          <div style={{ display: 'flex', gap: 8 }}>
            {['en', 'ru'].map(lang => {
              const active = locale === lang
              return (
                <button
                  key={lang}
                  onClick={() => setLocale(lang)}
                  style={{
                    flex: 1, padding: '9px 12px', borderRadius: 6,
                    fontSize: 11, fontWeight: 700, letterSpacing: 1,
                    cursor: 'pointer',
                    fontFamily: 'JetBrains Mono, monospace',
                    background: active ? 'rgba(0,255,136,0.1)' : 'transparent',
                    border: `1px solid ${active ? 'rgba(0,255,136,0.4)' : 'rgba(0,255,136,0.12)'}`,
                    color: active ? C.accent : C.textDim,
                    boxShadow: active ? '0 0 10px rgba(0,255,136,0.12)' : 'none',
                    transition: 'all 0.14s',
                  }}
                >
                  {lang === 'en' ? 'ENGLISH' : 'РУССКИЙ'}
                </button>
              )
            })}
          </div>
        </Card>

        <button
          onClick={save}
          disabled={loading}
          style={{
            width: '100%', padding: '12px 14px', borderRadius: 7,
            fontSize: 12, fontWeight: 700, letterSpacing: 1.5,
            cursor: loading ? 'wait' : 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            background: saved ? 'rgba(16,185,129,0.1)' : 'rgba(0,255,136,0.08)',
            border: `1px solid ${saved ? 'rgba(16,185,129,0.4)' : 'rgba(0,255,136,0.35)'}`,
            color: saved ? '#10b981' : C.accent,
            boxShadow: saved ? '0 0 12px rgba(16,185,129,0.15)' : '0 0 12px rgba(0,255,136,0.08)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => {
            if (!saved) {
              e.currentTarget.style.background = 'rgba(0,255,136,0.14)'
              e.currentTarget.style.boxShadow = '0 0 18px rgba(0,255,136,0.2)'
            }
          }}
          onMouseLeave={e => {
            if (!saved) {
              e.currentTarget.style.background = 'rgba(0,255,136,0.08)'
              e.currentTarget.style.boxShadow = '0 0 12px rgba(0,255,136,0.08)'
            }
          }}
        >
          <Check size={14} style={{ opacity: saved ? 1 : 0.6 }} />
          {saved ? tr('settings.saved').toUpperCase() : tr('settings.save').toUpperCase()}
        </button>

      </div>
    </div>
  )
}
