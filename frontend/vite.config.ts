import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // accesible desde fuera del contenedor
    port: 5173,
    watch: {
      usePolling: true, // fiable para hot-reload sobre volúmenes montados en Docker
    },
  },
});
