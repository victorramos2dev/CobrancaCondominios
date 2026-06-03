import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

/**
 * Decode a JWT payload (no verification — trust only for UI role checks).
 * The backend still validates the signature on every request.
 */
function decodePayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return {}
  }
}

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => localStorage.getItem('access_token'))
  const [refresh, setRefresh] = useState(() => localStorage.getItem('refresh_token'))
  const [user, setUser]     = useState(() => {
    const t = localStorage.getItem('access_token')
    return t ? decodePayload(t) : null
  })

  // Inject / remove the Authorization header globally
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  }, [token])

  /**
   * Intercept 401 responses and try to refresh the token automatically.
   * If refresh also fails, the user is logged out.
   */
  useEffect(() => {
    const id = api.interceptors.response.use(
      (res) => res,
      async (err) => {
        const original = err.config
        if (err.response?.status === 401 && !original._retry && refresh) {
          original._retry = true
          try {
            const { data } = await api.post('/api/token/refresh/', { refresh })
            localStorage.setItem('access_token', data.access)
            setToken(data.access)
            setUser(decodePayload(data.access))
            original.headers['Authorization'] = `Bearer ${data.access}`
            return api(original)
          } catch {
            logout()
          }
        }
        return Promise.reject(err)
      }
    )
    return () => api.interceptors.response.eject(id)
  }, [refresh])

  const login = useCallback(async (username, password) => {
    const { data } = await api.post('/api/token/', { username, password })
    localStorage.setItem('access_token',  data.access)
    localStorage.setItem('refresh_token', data.refresh)
    setToken(data.access)
    setRefresh(data.refresh)
    setUser(decodePayload(data.access))
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
    setRefresh(null)
    setUser(null)
  }, [])

  const isAdmin = user?.tipo === 'administrador'
  const isAuthenticated = Boolean(token)

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
