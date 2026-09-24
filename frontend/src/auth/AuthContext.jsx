import { createContext, useContext, useEffect, useState } from 'react'
import { getCurrentUser, loginRequest } from '../api/authApi'

const TOKEN_KEY = 'attendance_access_token'
const USER_KEY = 'attendance_current_user'
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem(USER_KEY)
    return savedUser ? JSON.parse(savedUser) : null
  })
  const [isLoading, setIsLoading] = useState(Boolean(token && !user))

  useEffect(() => {
    if (!token || user) {
      setIsLoading(false)
      return
    }

    getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser)
        localStorage.setItem(USER_KEY, JSON.stringify(currentUser))
      })
      .catch(() => logout())
      .finally(() => setIsLoading(false))
  }, [token, user])

  async function login(credentials) {
    const data = await loginRequest(credentials)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
    setIsLoading(false)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, isAuthenticated: Boolean(token && user), login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
