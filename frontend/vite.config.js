import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// host:true -> accesible desde fuera del contenedor (Docker)
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true, // necesario para hot-reload en bind-mount Docker
    },
  },
})
