import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Redirige todas estas rutas al backend durante desarrollo
      '/signin':        'http://localhost:8000',
      '/signup':        'http://localhost:8000',
      '/pacientes':     'http://localhost:8000',
      '/medicamentos':  'http://localhost:8000',
      '/recordatorios': 'http://localhost:8000',
      '/tomas':         'http://localhost:8000',
      '/resumen':       'http://localhost:8000',
      '/historial':     'http://localhost:8000',
    },
  },
  // En Docker usa la variable de entorno VITE_API_URL
  define: {
    'process.env.REACT_APP_API_URL': JSON.stringify(process.env.VITE_API_URL || ''),
  },
})