// Instancia axios central.
// - baseURL viene de VITE_API_URL (inyectada en build/dev).
// - Interceptor request: adjunta el JWT del localStorage en Authorization.
// - Interceptor response: si 401, limpia token y redirige a /login.
import axios from 'axios'

// baseURL:
//  - dev: VITE_API_URL = http://localhost:8000 (backend expuesto por compose)
//  - prod: VITE_API_URL = "" -> rutas relativas (/api) que nginx proxya al
//    backend; así NO se hardcodea la IP pública de EC2 (cambia cada sesión).
//  - sin variable definida: cae a localhost (?? distingue "" de undefined).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      // Evita bucle si ya estamos en login.
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
