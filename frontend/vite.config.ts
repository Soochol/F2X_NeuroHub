import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true, // 외부 접속 허용 (0.0.0.0)
    port: 3000,
    hmr: {
      // HMR WebSocket - use same port as dev server
      // Setting to false disables HMR WebSocket errors when port is in use
      protocol: 'ws',
      host: 'localhost',
    },
    proxy: {
      // WebSocket proxy for real-time metrics (must be before /api)
      '/api/v1/analytics/ws': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
      '/api': {
        // Docker 환경에서는 VITE_PROXY_TARGET 환경변수 사용
        // 로컬 개발: http://localhost:8000
        // Docker: http://backend:8000
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true, // Windows + Docker 환경에서 파일 변경 감지
      interval: 1000,
    },
  },
})
