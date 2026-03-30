import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Write App.tsx - ultra minimal, no imports except React
app_tsx = '''import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState('Loading...')

  useEffect(() => {
    fetch('/f1/api/health')
      .then(r => r.json())
      .then(d => setStatus('API: ' + d.status))
      .catch(() => setStatus('API: offline'))
  }, [])

  return (
    <div style={{
      backgroundColor: '#0a0a0f',
      color: '#ffffff',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>Pitwall.ai</h1>
      <p style={{ color: '#e10600', fontSize: '1.5rem', marginBottom: '2rem' }}>F1 Analytics Dashboard</p>
      <div style={{
        backgroundColor: '#1e1e2e',
        padding: '2rem',
        borderRadius: '12px',
        border: '1px solid #333',
        textAlign: 'center' as const,
        maxWidth: '500px'
      }}>
        <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Coming Soon - v2.0</p>
        <p style={{ color: '#888' }}>{status}</p>
        <p style={{ color: '#666', marginTop: '1rem', fontSize: '0.8rem' }}>2026 Season Data Pipeline Active</p>
      </div>
    </div>
  )
}

export default App
'''

# 2. Write main.tsx
main_tsx = '''import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

const rootEl = document.getElementById('root')
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <App />
    </StrictMode>
  )
} else {
  console.error('Root element not found')
}
'''

# 3. Write index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pitwall.ai - F1 Analytics</title>
    <style>body{margin:0;padding:0;background:#0a0a0f;}</style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/f1/src/main.tsx"></script>
  </body>
</html>
'''

# 4. Write vite.config.js
vite_config = '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/f1/",
  build: {
    outDir: "dist",
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
});
'''

# Write all files
files = {
    f'{base}/frontend/src/App.tsx': app_tsx,
    f'{base}/frontend/src/main.tsx': main_tsx,
    f'{base}/frontend/index.html': index_html,
    f'{base}/frontend/vite.config.js': vite_config,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f'Wrote: {path}')

# Delete vite.config.ts if exists
ts_config = f'{base}/frontend/vite.config.ts'
if os.path.exists(ts_config):
    os.remove(ts_config)
    print(f'Deleted: {ts_config}')

print('All frontend source files written successfully')
