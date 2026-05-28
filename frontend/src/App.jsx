import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Labs from './pages/Labs'
import LabDetail from './pages/LabDetail'
import Settings from './pages/Settings'
import Phisher from './pages/Phisher'
import Messenger from './pages/Messenger'
import OnboardingModal from './components/OnboardingModal'

export default function App() {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!localStorage.getItem('sf_onboarding_done')) {
      setShowOnboarding(true)
    }
  }, [])

  return (
    <>
      <Navbar onOpenGuide={() => setShowOnboarding(true)} />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/labs" element={<Labs />} />
        <Route path="/labs/:labId" element={<LabDetail />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/phisher" element={<Phisher />} />
        <Route path="/messenger" element={<Messenger />} />
      </Routes>
      {showOnboarding && (
        <OnboardingModal
          onClose={() => setShowOnboarding(false)}
          onDone={() => {
            localStorage.setItem('sf_onboarding_done', '1')
            setShowOnboarding(false)
            navigate('/labs')
          }}
        />
      )}
    </>
  )
}
