import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend'),
    },
  },
  build: {
    manifest: true,
    outDir: 'static/build',
    rollupOptions: {
      input: 'frontend/app.tsx',
    },
  },
  server: {
    // Cross-Inertia picks a free port and passes it via --port; use the URL it
    // exports so asset URLs emitted in dev point at Vite, not the FastAPI app.
    origin: process.env.INERTIA_VITE_URL,
    strictPort: true,
  },
})
