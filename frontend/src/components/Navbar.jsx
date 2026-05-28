import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useApp } from '../store'
import { t } from '../i18n'
import { Shield, Globe, LogOut, HelpCircle, MessageSquare } from 'lucide-react'

const C = {
  accent:    '#00ff88',
  border:    'rgba(0,255,136,0.12)',
  muted:     'rgba(0,255,136,0.4)',
  textDim:   'rgba(212,245,226,0.45)',
  text:      '#d4f5e2',
  bg:        'rgba(6,10,15,0.97)',
  glow:      '0 0 10px rgba(0,255,136,0.18)',
}

function NavLink({ to, children, isLabDetail }) {
  const location = useLocation()
  const active = location.pathname === to || location.pathname.startsWith(to + '/')
  const [hov, setHov] = useState(false)

  return (
    <Link
      to={to}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        fontSize: isLabDetail ? 11 : 12,
        fontWeight: 700,
        letterSpacing: 1,
        textDecoration: 'none',
        padding: isLabDetail ? '3px 8px' : '5px 10px',
        borderRadius: 5,
        color: active ? C.accent : hov ? C.text : C.textDim,
        background: active ? 'rgba(0,255,136,0.07)' : hov ? 'rgba(0,255,136,0.04)' : 'transparent',
        boxShadow: active ? C.glow : 'none',
        borderBottom: active ? `1px solid rgba(0,255,136,0.35)` : '1px solid transparent',
        transition: 'all 0.13s',
        fontFamily: 'JetBrains Mono, monospace',
      }}
    >
      {children}
    </Link>
  )
}

export default function Navbar({ onOpenGuide }) {
  const { user, locale, toggleLocale, logout } = useApp()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const isLabDetail = /^\/labs\/[^/]+$/.test(location.pathname)
  const height = isLabDetail ? 44 : 56

  return (
    <nav style={{
      background: C.bg,
      backdropFilter: 'blur(14px)',
      borderBottom: `1px solid ${C.border}`,
      padding: '0 24px',
      height,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      fontFamily: 'JetBrains Mono, monospace',
    }}>

      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <Link to={user ? '/labs' : '/'} style={{ display: 'flex', alignItems: 'center', gap: 7, textDecoration: 'none' }}>
          <Shield
            size={isLabDetail ? 16 : 20}
            color={C.accent}
            style={{ filter: `drop-shadow(0 0 5px rgba(0,255,136,0.5))` }}
          />
          <span style={{
            fontSize: isLabDetail ? 13 : 15,
            fontWeight: 700,
            letterSpacing: 1.5,
            color: C.accent,
            fontFamily: 'JetBrains Mono, monospace',
          }}>
            SOCIAL<span style={{ color: '#e8f5ee' }}>FORGE</span>
          </span>
        </Link>

        {user && !isLabDetail && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 2, marginLeft: 8 }}>
            <NavLink to="/labs" isLabDetail={isLabDetail}>
              {t('nav.labs', locale).toUpperCase()}
            </NavLink>
            <NavLink to="/settings" isLabDetail={isLabDetail}>
              {t('nav.settings', locale).toUpperCase()}
            </NavLink>
          </div>
        )}

        {user && isLabDetail && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 2, marginLeft: 4 }}>
            <NavLink to="/labs" isLabDetail={isLabDetail}>LABS</NavLink>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <button
          onClick={onOpenGuide}
          style={{
            display: 'flex', alignItems: 'center', gap: 4,
            fontSize: 10, fontWeight: 700, letterSpacing: 1,
            padding: '4px 9px', borderRadius: 5,
            background: 'transparent',
            border: '1px solid rgba(0,255,136,0.15)',
            color: C.muted,
            cursor: 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            transition: 'all 0.13s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'rgba(0,255,136,0.35)'
            e.currentTarget.style.color = C.accent
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'rgba(0,255,136,0.15)'
            e.currentTarget.style.color = C.muted
          }}
        >
          <HelpCircle size={11} />
          {t('nav.guide', locale).toUpperCase()}
        </button>
        <button
          onClick={toggleLocale}
          style={{
            display: 'flex', alignItems: 'center', gap: 4,
            fontSize: 10, fontWeight: 700, letterSpacing: 1,
            padding: '4px 9px', borderRadius: 5,
            background: 'transparent',
            border: '1px solid rgba(0,255,136,0.15)',
            color: C.muted,
            cursor: 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            transition: 'all 0.13s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'rgba(0,255,136,0.35)'
            e.currentTarget.style.color = C.accent
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'rgba(0,255,136,0.15)'
            e.currentTarget.style.color = C.muted
          }}
        >
          <Globe size={11} />
          {locale.toUpperCase()}
        </button>

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              fontSize: 11, fontWeight: 700,
              color: C.accent,
              background: 'rgba(0,255,136,0.06)',
              border: '1px solid rgba(0,255,136,0.2)',
              padding: '3px 9px', borderRadius: 5,
              letterSpacing: 0.5,
              fontFamily: 'JetBrains Mono, monospace',
            }}>
              {user.username}
            </span>
            <button
              onClick={handleLogout}
              title={t('nav.logout', locale).toUpperCase()}
              style={{
                display: 'flex', alignItems: 'center', gap: 4,
                fontSize: 10, fontWeight: 700,
                padding: '4px 9px', borderRadius: 5,
                background: 'transparent',
                border: '1px solid rgba(255,51,102,0.15)',
                color: 'rgba(255,51,102,0.5)',
                cursor: 'pointer',
                fontFamily: 'JetBrains Mono, monospace',
                transition: 'all 0.13s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'rgba(255,51,102,0.4)'
                e.currentTarget.style.color = '#ff3366'
                e.currentTarget.style.background = 'rgba(255,51,102,0.06)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'rgba(255,51,102,0.15)'
                e.currentTarget.style.color = 'rgba(255,51,102,0.5)'
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <LogOut size={11} />
              {!isLabDetail && t('nav.logout', locale).toUpperCase()}
            </button>
          </div>
        ) : (
          <Link to="/login" style={{
            fontSize: 11, fontWeight: 700, letterSpacing: 1,
            padding: '5px 14px', borderRadius: 5, textDecoration: 'none',
            background: 'rgba(0,255,136,0.1)',
            border: '1px solid rgba(0,255,136,0.3)',
            color: C.accent,
            fontFamily: 'JetBrains Mono, monospace',
            transition: 'all 0.13s',
          }}>
            {t('nav.login', locale).toUpperCase()}
          </Link>
        )}
      </div>
    </nav>
  )
}
