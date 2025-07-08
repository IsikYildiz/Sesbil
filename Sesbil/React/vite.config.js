import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react(),
  ],
  base: '/' ,
  build: {
    outDir: '../wwwroot/react',
    emptyOutDir: true,
  },
  test: {
    globals: true,
    environment: 'jsdom'
  }
})
