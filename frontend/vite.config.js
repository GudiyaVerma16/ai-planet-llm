import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  preview: {
    port: parseInt(process.env.PORT) || 3000,
    host: '0.0.0.0',
    strictPort: false,
    allowedHosts: [
      'ai-planet-llm-1.onrender.com',
      '.onrender.com' // Allow all Render subdomains
    ]
  }
})
