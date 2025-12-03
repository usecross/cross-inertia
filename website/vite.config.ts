import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ isSsrBuild }) => ({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend'),
    },
  },
  build: {
    manifest: !isSsrBuild,
    outDir: isSsrBuild ? 'static/build/ssr' : 'static/build',
    rollupOptions: {
      input: isSsrBuild ? 'frontend/ssr.tsx' : 'frontend/app.tsx',
    },
  },
  ssr: {
    // Bundle all dependencies into the SSR build so no node_modules needed at runtime
    noExternal: isSsrBuild ? true : ['shiki', '@inertiajs/react'],
  },
  server: {
    port: 5188,
    strictPort: true,
  },
}))
