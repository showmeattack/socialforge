import { Link } from 'react-router-dom'
import { useApp } from '../store'
import { t } from '../i18n'
import { Shield, Users, Mail, Phone, Terminal, ChevronRight } from 'lucide-react'

export default function Landing() {
  const { locale, user } = useApp()
  const tr = (key) => t(key, locale)
  const features = tr('landing.features')

  const icons = [<Terminal size={28} />, <Users size={28} />, <Phone size={28} />]

  return (
    <div>
      {/* Hero */}
      <div className="scanlines" style={{
        minHeight: 'calc(100vh - 56px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '60px 24px',
        background: `
          radial-gradient(ellipse at 50% 0%, rgba(16, 185, 129, 0.08) 0%, transparent 60%),
          radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
          var(--bg-primary)
        `,
      }}>
        <div style={{ maxWidth: 800 }}>
          <div style={{ marginBottom: 24 }}>
            <Shield size={48} color="var(--accent)" style={{ filter: 'drop-shadow(0 0 20px rgba(16,185,129,0.3))' }} />
          </div>

          <h1 className="mono" style={{
            fontSize: 'clamp(40px, 6vw, 64px)',
            fontWeight: 700,
            letterSpacing: 2,
            marginBottom: 16,
            color: 'var(--accent)',
            textShadow: '0 0 40px rgba(16,185,129,0.2)',
          }}>
            {tr('landing.title')}
          </h1>

          <p style={{
            fontSize: 'clamp(16px, 2.5vw, 22px)',
            color: 'var(--text-secondary)',
            marginBottom: 12,
            lineHeight: 1.6,
          }}>
            {tr('landing.subtitle')}
          </p>

          <p className="mono" style={{
            fontSize: 14,
            color: 'var(--text-muted)',
            marginBottom: 40,
          }}>
            {'> '}{tr('landing.tagline')}
            <span style={{ animation: 'blink 1s step-end infinite', borderRight: '2px solid var(--accent)', paddingLeft: 2 }}>&nbsp;</span>
          </p>

          <Link
            to={user ? '/labs' : '/register'}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--accent)',
              color: '#000',
              padding: '14px 32px',
              borderRadius: 8,
              fontSize: 16,
              fontWeight: 600,
              textDecoration: 'none',
              transition: 'all 0.2s',
              boxShadow: '0 0 30px rgba(16,185,129,0.2)',
            }}
          >
            {tr('landing.cta')}
            <ChevronRight size={18} />
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="container" style={{ padding: '80px 24px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 24,
        }}>
          {Array.isArray(features) && features.map((f, i) => (
            <div key={i} className="card" style={{ textAlign: 'center', padding: 32 }}>
              <div style={{
                width: 56,
                height: 56,
                borderRadius: 12,
                background: 'var(--accent-glow)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                color: 'var(--accent)',
              }}>
                {icons[i]}
              </div>
              <h3 style={{ fontSize: 18, marginBottom: 8 }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '24px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: 12,
      }}>
        <span className="mono">SocialForge v0.1.0</span> — Social Engineering CTF Platform
      </footer>
    </div>
  )
}
