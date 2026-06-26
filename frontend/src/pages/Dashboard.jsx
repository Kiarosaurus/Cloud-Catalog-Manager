// Dashboard: lista los usuarios, permite crear/editar/eliminar.
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Logo, IconPlus, IconEdit, IconTrash, IconLogout, IconUsers } from '../components/icons'

// Badge de estado del usuario.
function statusBadge(status) {
  return status === 'inactivo'
    ? { cls: 'badge-out', label: 'Inactivo' }
    : { cls: 'badge-ok', label: 'Activo' }
}

// Iniciales para el fallback del avatar (máx. 2 letras).
function initials(name) {
  return (name || '?')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
}

// Avatar con presigned URL; si falla la carga (URL expirada / sin foto)
// muestra las iniciales en vez del icono de imagen rota.
function Avatar({ url, name }) {
  const [failed, setFailed] = useState(false)
  if (!url || failed) {
    return <span className="avatar-empty">{initials(name)}</span>
  }
  return (
    <img className="avatar" src={url} alt={name} onError={() => setFailed(true)} />
  )
}

export default function Dashboard() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadUsers() {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get('/api/users/')
      setUsers(data)
    } catch (err) {
      setError('No se pudieron cargar los usuarios')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  async function handleDelete(id) {
    if (!window.confirm('¿Eliminar este usuario?')) return
    try {
      await api.delete(`/api/users/${id}`)
      setUsers((prev) => prev.filter((u) => u.id !== id))
    } catch (err) {
      alert('Error al eliminar el usuario')
    }
  }

  return (
    <div className="app-shell">
      <header className="appbar">
        <div className="appbar-inner">
          <div className="brand">
            <span className="brand-logo">
              <Logo size={22} />
            </span>
            <div>
              <div className="brand-name">Usuarios Admin</div>
              <div className="brand-sub">Panel de administración</div>
            </div>
          </div>
          <div className="actions">
            <button className="btn btn-primary" onClick={() => navigate('/users/new')}>
              <IconPlus width={16} height={16} />
              <span className="label">Nuevo usuario</span>
            </button>
            <button className="btn btn-ghost" onClick={logout} title="Cerrar sesión">
              <IconLogout width={16} height={16} />
              <span className="label">Salir</span>
            </button>
          </div>
        </div>
      </header>

      <main className="container">
        <div className="toolbar">
          <h2>Usuarios</h2>
          {!loading && <span className="count-chip">{users.length}</span>}
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="panel">
            <div className="loading">
              <span className="spinner" /> Cargando usuarios…
            </div>
          </div>
        ) : users.length === 0 ? (
          <div className="panel">
            <div className="empty-state">
              <span className="empty-icon">
                <IconUsers width={30} height={30} />
              </span>
              <h3>Aún no hay usuarios</h3>
              <p>Crea el primer usuario para empezar a administrar el sistema.</p>
              <button className="btn btn-primary" onClick={() => navigate('/users/new')}>
                <IconPlus width={16} height={16} /> Crear usuario
              </button>
            </div>
          </div>
        ) : (
          <div className="panel">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Teléfono</th>
                  <th>Estado</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => {
                  const badge = statusBadge(u.status)
                  return (
                    <tr key={u.id}>
                      <td>
                        <div className="user-cell">
                          <Avatar url={u.profile_image_url} name={u.name} />
                          <div>
                            <div className="cell-name">{u.name}</div>
                            <div className="muted" style={{ fontSize: '0.82rem' }}>
                              {u.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="code-chip">{u.role}</span>
                      </td>
                      <td>{u.phone || <span className="muted">—</span>}</td>
                      <td>
                        <span className={`badge ${badge.cls}`}>{badge.label}</span>
                      </td>
                      <td>
                        <div className="row-actions">
                          <button
                            className="icon-btn"
                            title="Editar"
                            onClick={() => navigate(`/users/${u.id}/edit`)}
                          >
                            <IconEdit width={16} height={16} />
                          </button>
                          <button
                            className="icon-btn danger"
                            title="Eliminar"
                            onClick={() => handleDelete(u.id)}
                          >
                            <IconTrash width={16} height={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
