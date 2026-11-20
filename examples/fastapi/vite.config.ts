import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

const viteHost = '127.0.0.1'
const vitePortValue = process.env.INERTIA_VITE_PORT ?? '5173'
const vitePort = Number(vitePortValue)
const launcherId = process.env.INERTIA_VITE_LAUNCHER_ID

if (!vitePortValue || vitePortValue.length > 5 || /[^0-9]/.test(vitePortValue) ||
    vitePort < 1 || vitePort > 65535) {
  throw new Error(`INERTIA_VITE_PORT must be an integer from 1 to 65535 (got ${JSON.stringify(vitePortValue)}).`)
}

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
    host: viteHost,
    port: vitePort,
    origin: `http://${viteHost}:${vitePort}`,
    strictPort: true,
    headers: launcherId ? { 'X-Inertia-Vite-Launcher': launcherId } : undefined,
  },
})
