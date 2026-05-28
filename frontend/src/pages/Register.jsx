import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useApp } from '../store'
import { t } from '../i18n'
import { api } from '../api'
import { Shield, UserPlus } from 'lucide-react'

export default function Register() {
  const { locale, login } = useApp()
  const navigate = useNavigate()
  const tr = (key) => t(key, locale)
  const [form, setForm] = useState({ username: '', email: '', password: '', display_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.register({ ...form, locale })
      login(data)
      navigate('/labs')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
    }}>
      <div className="card" style={{ width: 400, padding: 40 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Shield size={32} color="var(--accent)" />
          <h1 style={{ fontSize: 24, marginTop: 12 }}>{tr('auth.register')}</h1>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
              {tr('auth.username')}
            </label>
            <input
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              style={{ width: '100%' }}
              required
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
              {tr('auth.email')}
            </label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              style={{ width: '100%' }}
              required
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
              {tr('auth.displayName')}
            </label>
            <input
              value={form.display_name}
              onChange={e => setForm({ ...form, display_name: e.target.value })}
              style={{ width: '100%' }}
            />
          </div>
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
              {tr('auth.password')}
            </label>
            <input
              type="password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              style={{ width: '100%' }}
              required
            />
          </div>

          {error && (
            <div style={{
              background: 'var(--red-glow)',
              border: '1px solid rgba(239,68,68,0.3)',
              color: 'var(--red)',
              borderRadius: 6,
              padding: '10px 14px',
              fontSize: 13,
              marginBottom: 16,
            }}>
              {error}
            </div>
          )}

          <button type="submit" className="btn-primary" disabled={loading}
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 12 }}>
            <UserPlus size={16} />
            {loading ? '...' : tr('auth.register')}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          {tr('auth.hasAccount')} <Link to="/login">{tr('auth.login')}</Link>
        </p>
      </div>
    </div>
  )
}
