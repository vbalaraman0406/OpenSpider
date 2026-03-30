import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

app_tsx = """import React from 'react';

function App() {
  return (
    <div style={{ backgroundColor: '#0a0a0f', color: '#ffffff', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, sans-serif' }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '1rem' }}>Pitwall.ai</h1>
      <p style={{ fontSize: '1.5rem', color: '#e10600', fontWeight: 600 }}>F1 Analytics Dashboard</p>
      <p style={{ fontSize: '1rem', color: '#888', marginTop: '1rem' }}>Loading race data...</p>
      <div style={{ marginTop: '2rem', padding: '1rem 2rem', backgroundColor: '#1e1e2e', borderRadius: '8px', border: '1px solid #333' }}>
        <p style={{ color: '#4ade80' }}>React is rendering correctly</p>
        <p style={{ color: '#4ade80' }}>GCP App Engine deployment working</p>
        <p style={{ color: '#facc15' }}>Full dashboard coming soon...</p>
      </div>
    </div>
  );
}

export default App;
"""

app_path = os.path.join(base, 'frontend', 'src', 'App.tsx')
with open(app_path, 'w') as f:
    f.write(app_tsx)
print(f'Wrote minimal App.tsx to {app_path}')
print(f'Content length: {len(app_tsx)}')

with open(app_path, 'r') as f:
    content = f.read()
print(f'Verified: {len(content)} bytes')
print(content[:300])
