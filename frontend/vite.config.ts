import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

declare const process: any;

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = process.env.BACKEND_URL || env.BACKEND_URL || 'http://api:8000'
  const wsTarget = (process.env.WS_BACKEND_URL || env.WS_BACKEND_URL || apiTarget).replace(/^http/, 'ws')

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
        '/ws': {
          target: wsTarget,
          ws: true,
        }
      }
    }
  }
})

