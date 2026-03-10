import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 5173,              // fixed port for the dev server
    proxy: {
      // Forward all API calls to the Flask backend running on port 5000
      '/auth': 'http://127.0.0.1:5000',
      '/student': 'http://127.0.0.1:5000',
      '/company': 'http://127.0.0.1:5000',
      '/admin': 'http://127.0.0.1:5000',
      '/drive': 'http://127.0.0.1:5000',
      '/application': 'http://127.0.0.1:5000',
      '/api': 'http://127.0.0.1:5000'
    }
  }
})
