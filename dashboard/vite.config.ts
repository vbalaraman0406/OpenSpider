import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        tailwindcss(),
        react(),
    ],
    envDir: '../', // CRITICAL: This allows Vite to see the .env file in the OpenSpider root directory
    server: {
        port: 5173,
        proxy: {
            '/api': 'http://localhost:4001',
        }
    }
});
