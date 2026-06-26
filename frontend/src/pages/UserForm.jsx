// Formulario de creación / edición de usuario con upload de foto de perfil a S3.
// En modo edición carga los datos existentes; la imagen solo se reemplaza
// si se selecciona un archivo nuevo.
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import { IconBack, IconUpload } from '../components/icons'

const EMPTY = { name: '', email: '', role: 'user', status: 'activo', phone: '' }

export default function UserForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY)
  const [imageFile, setImageFile] = useState(null)
  const [currentImage, setCurrentImage] = useState(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!isEdit) return
    api
      .get(`/api/users/${id}`)
      .then(({ data }) => {
        setForm({
          name: data.name,
          email: data.email,
          role: data.role,
          status: data.status,
          phone: data.phone || '',
        })
        setCurrentImage(data.profile_image_url)
      })
      .catch(() => setError('No se pudo cargar el usuario'))
  }, [id, isEdit])

  // Preview local del archivo recién seleccionado (object URL).
  const previewUrl = useMemo(
    () => (imageFile ? URL.createObjectURL(imageFile) : currentImage),
    [imageFile, currentImage]
  )

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)

    // multipart/form-data: campos + archivo opcional.
    const body = new FormData()
    body.append('name', form.name)
    body.append('email', form.email)
    body.append('role', form.role)
    body.append('status', form.status)
    body.append('phone', form.phone)
    if (imageFile) {
      body.append('image', imageFile)
    }

    try {
      if (isEdit) {
        await api.put(`/api/users/${id}`, body)
      } else {
        await api.post('/api/users/', body)
      }
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar el usuario')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="app-shell">
      <main className="container">
        <div className="page-head">
          <button className="icon-btn" onClick={() => navigate('/')} title="Volver">
            <IconBack width={18} height={18} />
          </button>
          <h2>{isEdit ? 'Editar usuario' : 'Nuevo usuario'}</h2>
        </div>

        <form className="form-card" onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}

          <label className="field">
            <span>Nombre</span>
            <input
              className="input"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Juan Pérez"
              required
            />
          </label>

          <label className="field">
            <span>Email</span>
            <input
              className="input"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="juan@example.com"
              required
            />
          </label>

          <div className="form-grid">
            <label className="field">
              <span>Rol</span>
              <select className="input" name="role" value={form.role} onChange={handleChange}>
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </label>
            <label className="field">
              <span>Estado</span>
              <select className="input" name="status" value={form.status} onChange={handleChange}>
                <option value="activo">activo</option>
                <option value="inactivo">inactivo</option>
              </select>
            </label>
          </div>

          <label className="field">
            <span>
              Teléfono <span className="hint">(opcional)</span>
            </span>
            <input
              className="input"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="+51 999 999 999"
            />
          </label>

          <div className="field">
            <span>
              Foto de perfil{' '}
              {isEdit && <span className="hint">(dejar vacío para conservar la actual)</span>}
            </span>
            <label className="dropzone">
              {previewUrl ? (
                <img className="dropzone-preview" src={previewUrl} alt="vista previa" />
              ) : (
                <span className="dropzone-placeholder">
                  <IconUpload width={22} height={22} />
                </span>
              )}
              <span className="dropzone-text">
                <strong>{imageFile ? imageFile.name : 'Subir foto de perfil'}</strong>
                <span>JPG, PNG, WEBP o GIF · click para elegir</span>
              </span>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setImageFile(e.target.files[0] || null)}
              />
            </label>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? (
                <>
                  <span className="spinner" /> Guardando…
                </>
              ) : (
                'Guardar usuario'
              )}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => navigate('/')}>
              Cancelar
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
