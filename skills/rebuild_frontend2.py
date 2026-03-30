import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
FRONTEND = os.path.join(BASE, 'frontend')

app_tsx = '''import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState('Loading...')
  
  useEffect(() => {
    setStatus('React is running!')
    fetch('/f1/api/health')
      .then(r => r.json())
      .then(d => setStatus('API: ' + JSON.stringify(d)))
      .catch(e => setStatus('API error: ' + e.message))
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0a0f',
      color: '#ffffff',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '2rem'
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem', fontWeight: 700 }}>
        Pitwall<span style={{ color: '#e10600' }}>.ai</span>
      </h1>
      <p style={{ fontSize: '1.2rem', color: '#e10600', marginBottom: '2rem' }}>
        F1 Analytics Dashboard
      </p>
      <div style={{
        backgroundColor: '#1a1a2e',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '600px',
        width: '100%',
        border: '1px solid #2a2a3e'
      }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>System Status</h2>
        <p style={{ color: '#00ff88', fontSize: '1.1rem' }}>{status}</p>
        <div style={{ marginTop: '1.5rem', color: '#888' }}>
          <p>Version: f1-final-fix</p>
        </div>
      </div>
      <div style={{
        marginTop: '2rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '1rem',
        maxWidth: '600px',
        width: '100%'
      }}>
        {['Australian GP', 'Chinese GP', 'Japanese GP'].map(race => (
          <div key={race} style={{
            backgroundColor: '#1a1a2e',
            borderRadius: '8px',
            padding: '1rem',
            textAlign: 'center' as const,
            border: '1px solid #2a2a3e'
          }}>
            <p style={{ color: '#e10600', fontWeight: 600 }}>{race}</p>
            <p style={{ color: '#666', fontSize: '0.8rem' }}>Coming Soon</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
'''

main_tsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

const rootEl = document.getElementById('root')
if (rootEl) {
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
} else {
  document.body.innerHTML = '<h1 style="color:red">ERROR: root element not found</h1>'
}
'''

vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/f1/',
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})
'''

index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pitwall.ai - F1 Analytics</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { background-color: #0a0a0f; color: #fff; font-family: Inter, system-ui, sans-serif; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/f1/src/main.tsx"></script>
  </body>
</html>
'''

with open(os.path.join(FRONTEND, 'src', 'App.tsx'), 'w') as f:
    f.write(app_tsx)
print('Wrote App.tsx')

with open(os.path.join(FRONTEND, 'src', 'main.tsx'), 'w') as f:
    f.write(main_tsx)
print('Wrote main.tsx')

with open(os.path.join(FRONTEND, 'index.html'), 'w') as f:
    f.write(index_html)
print('Wrote index.html')

with open(os.path.join(FRONTEND, 'vite.config.js'), 'w') as f:
    f.write(vite_config)
print('Wrote vite.config.js')

ts_path = os.path.join(FRONTEND, 'vite.config.ts')
if os.path.exists(ts_path):
    os.remove(ts_path)
    print('Deleted vite.config.ts')

# Clean old dist assets
assets_dir = os.path.join(FRONTEND, 'dist', 'assets')
if os.path.exists(assets_dir):
    for f in os.listdir(assets_dir):
        os.remove(os.path.join(assets_dir, f))
    print('Cleaned old dist/assets/')

print('All frontend files written. Ready to build.')
