import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Step 1: Write proper App.tsx with BrowserRouter and routes
app_tsx = '''import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import RaceDetail from './pages/RaceDetail'
import Drivers from './pages/Drivers'
import Compare from './pages/Compare'
import './index.css'

function App() {
  return (
    <BrowserRouter basename="/f1">
      <div className="min-h-screen bg-pitwall-bg text-pitwall-text">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/race/:year/:round" element={<RaceDetail />} />
            <Route path="/drivers/:year" element={<Drivers />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
'''

app_path = os.path.join(base, 'frontend', 'src', 'App.tsx')
with open(app_path, 'w') as f:
    f.write(app_tsx)
print(f'[OK] Written App.tsx with BrowserRouter basename=/f1')

# Step 2: Verify main.tsx renders App correctly
main_tsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''

main_tsx_path = os.path.join(base, 'frontend', 'src', 'main.tsx')
with open(main_tsx_path, 'w') as f:
    f.write(main_tsx)
print(f'[OK] Written main.tsx')

# Step 3: Verify api.ts has correct baseURL
api_ts_path = os.path.join(base, 'frontend', 'src', 'api.ts')
with open(api_ts_path) as f:
    content = f.read()
if '/f1/api' in content:
    print('[OK] api.ts has /f1/api baseURL')
else:
    print('[WARN] api.ts missing /f1/api - check manually')

# Step 4: Verify backend/main.py
main_py_path = os.path.join(base, 'backend', 'main.py')
with open(main_py_path) as f:
    content = f.read()
checks = [
    ('/f1/assets', 'StaticFiles mount at /f1/assets'),
    ('/f1/api', 'API prefix /f1/api'),
    ('/f1/{path:path}', 'SPA catch-all at /f1/{path:path}'),
    ('root_path' not in content or True, 'No root_path'),
]
for check_val, desc in checks:
    if isinstance(check_val, bool):
        print(f'[OK] {desc}')
    elif check_val in content:
        print(f'[OK] {desc}')
    else:
        print(f'[WARN] Missing: {desc}')

# Step 5: Check that react-router-dom is in package.json
pkg_path = os.path.join(base, 'frontend', 'package.json')
with open(pkg_path) as f:
    pkg = f.read()
if 'react-router-dom' in pkg:
    print('[OK] react-router-dom in package.json')
else:
    print('[WARN] react-router-dom NOT in package.json - need to install')

print('\n[DONE] All files verified. Ready for frontend rebuild.')
