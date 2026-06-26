// Contexto de autenticación: guarda el token en localStorage y expone
// login()/logout(). El estado isAuthenticated controla las rutas protegidas.
import { createContext, useContext, useState } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  async function login(username, password) {
    // El backend usa OAuth2PasswordRequestForm -> enviar x-www-form-urlencoded.
    const body = new URLSearchParams()
    body.append('username', username)
    body.append('password', password)

    const { data } = await api.post('/api/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
