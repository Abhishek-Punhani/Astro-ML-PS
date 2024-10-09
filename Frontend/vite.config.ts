import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import envCompatible from 'vite-plugin-env-compatible'
import fs from 'fs';
import path from 'path';
// https://vitejs.dev/config/
export default defineConfig({
  envPrefix:"REACT_APP_",
  plugins: [react(),envCompatible()],
  server: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'certs/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'certs/cert.pem')),
    },
    port: 5173,  // Your frontend port
    host: 'localhost',  // Or '0.0.0.0' if you need to access from other devices
  },
})



