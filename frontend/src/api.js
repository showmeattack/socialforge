const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Auth
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),

  // Labs
  getLabs: () => request('/labs'),
  getLab: (id) => request(`/labs/${id}`),
  startLab: (id, userId) => request(`/labs/${id}/start?user_id=${userId}`, { method: 'POST' }),
  resetLab: (id, userId) => request(`/labs/${id}/reset?user_id=${userId}`, { method: 'POST' }),
  getLabProgress: (id, userId) => request(`/labs/${id}/progress?user_id=${userId}`),

  // Session
  startSession: (userId, labId) => request('/session/start', { method: 'POST', body: JSON.stringify({ user_id: userId, lab_id: labId }) }),
  startSessionAll: (userId) => request('/session/start-all', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  currentSession: (userId, labId) => request(`/session/current?user_id=${userId}&lab_id=${labId}`),
  sessionStatus: (userId) => request(`/session/status?user_id=${userId}`),
  endSession: (userId, labId) => request('/session/end', { method: 'POST', body: JSON.stringify({ user_id: userId, lab_id: labId }) }),

  // Chat
  chat: (data) => request('/chat', { method: 'POST', body: JSON.stringify(data) }),

  // Flags
  submitFlag: (data) => request('/flags/submit', { method: 'POST', body: JSON.stringify(data) }),

  // Settings
  getSettings: () => request('/settings'),
  updateSettings: (data) => request('/settings', { method: 'POST', body: JSON.stringify(data) }),

}
