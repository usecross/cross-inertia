import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './frontend'),
    },
  },
  build: {
    manifest: true,
    outDir: 'static/build',
    rolldownOptions: {
      input: 'frontend/app.tsx',
    },
  },
  server: {
    host: '127.0.0.1',
    // Cross-Inertia picks a free port and passes it via --port; use the URL it
    // exports so asset URLs emitted in dev point at Vite, not the FastAPI app.
    origin: process.env.INERTIA_VITE_URL,
    strictPort: true,
  },
})
