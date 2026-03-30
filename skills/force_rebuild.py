import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Modify App.tsx with actual content change to force new hash
app_tsx = """import React from 'react';

const BUILD_ID = '""" + str(int(time.time())) + """';

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
        <p style={{ color: '#666', fontSize: '0.75rem', marginTop: '0.5rem' }}>Build: {BUILD_ID}</p>
      </div>
    </div>
  );
}

export default App;
"""

app_path = os.path.join(base, 'frontend', 'src', 'App.tsx')
with open(app_path, 'w') as f:
    f.write(app_tsx)
print(f'Wrote App.tsx with BUILD_ID runtime variable')

# Also ensure main.tsx doesn't import index.css (potential Tailwind issue)
main_tsx_path = os.path.join(base, 'frontend', 'src', 'main.tsx')
with open(main_tsx_path, 'r') as f:
    main_content = f.read()
print(f'main.tsx content:\n{main_content}')

# Check if index.css exists and what it contains
css_path = os.path.join(base, 'frontend', 'src', 'index.css')
if os.path.exists(css_path):
    with open(css_path, 'r') as f:
        css = f.read()
    print(f'index.css ({len(css)} bytes):\n{css[:500]}')
else:
    print('index.css does not exist')
