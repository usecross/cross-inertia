import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ isSsrBuild, command }) => ({
  plugins: [react()],
  root: 'frontend',
  // Use base path only for production builds, not for dev server
  base: command === 'serve' ? '/' : isSsrBuild ? '/' : '/static/build/',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend'),
    },
    // Dedupe to ensure single instance of @inertiajs/react (fixes usePage context issue)
    dedupe: ['@inertiajs/react', 'react', 'react-dom'],
  },
  build: {
    manifest: !isSsrBuild,
    outDir: isSsrBuild ? '../static/build/ssr' : '../static/build',
    rollupOptions: {
      input: isSsrBuild ? 'ssr.tsx' : 'app.tsx',
    },
  },
  ssr: {
    // Bundle all dependencies into the SSR build so no node_modules needed at runtime
    noExternal: isSsrBuild ? true : ['shiki', '@inertiajs/react'],
  },
  server: {
    port: 5173,
    strictPort: true,
  },
}))
