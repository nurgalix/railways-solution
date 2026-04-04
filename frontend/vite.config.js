import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // REST API
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // WebSocket  (vite dev proxy for WS)
      '/api/ws': {
        target:  'ws://localhost:8000',
        ws:      true,
        changeOrigin: true,
      },
    },
  },
});
