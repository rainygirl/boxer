import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/api': { target: 'http://127.0.0.1:4000', changeOrigin: true },
      '/auth/jwt': { target: 'http://127.0.0.1:4000', changeOrigin: true },
      '/accounts': { target: 'http://127.0.0.1:4000', changeOrigin: true },
    },
  },
});
