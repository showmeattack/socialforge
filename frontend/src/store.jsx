import { createContext, useContext, useState, useEffect } from 'react'

const AppContext = createContext()

export function AppProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('sf_user')
    return saved ? JSON.parse(saved) : null
  })
  const [locale, setLocale] = useState(() => {
    return localStorage.getItem('sf_locale') || 'en'
  })
  useEffect(() => {
    if (user) localStorage.setItem('sf_user', JSON.stringify(user))
    else localStorage.removeItem('sf_user')
  }, [user])

  useEffect(() => { localStorage.setItem('sf_locale', locale) }, [locale])

  const login = (userData) => setUser(userData)
  const logout = () => setUser(null)
  const toggleLocale = () => setLocale(l => l === 'en' ? 'ru' : 'en')

  return (
    <AppContext.Provider value={{ user, locale, login, logout, setLocale, toggleLocale }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  return useContext(AppContext)
}
