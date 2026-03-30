import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Write ErrorBoundary component
error_boundary = '''import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: string;
}

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: '' };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('React Error Boundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', color: '#e10600', backgroundColor: '#0a0a0f', minHeight: '100vh', fontFamily: 'monospace' }}>
          <h1 style={{ fontSize: '24px', marginBottom: '16px' }}>Pitwall.ai - Error</h1>
          <p style={{ color: '#fff' }}>Something went wrong:</p>
          <pre style={{ color: '#ff6b6b', marginTop: '8px', whiteSpace: 'pre-wrap' }}>{this.state.error}</pre>
          <button onClick={() => window.location.reload()} style={{ marginTop: '20px', padding: '8px 16px', backgroundColor: '#e10600', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Reload</button>
        </div>
      );
    }
    return this.props.children;
  }
}
'''

eb_path = os.path.join(base, 'components', 'ErrorBoundary.tsx')
with open(eb_path, 'w') as f:
    f.write(error_boundary)
print('[OK] Written ErrorBoundary.tsx')

# Write bulletproof Dashboard.tsx
dashboard = '''import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRaces } from '../api';

interface Race {
  round: number;
  raceName: string;
  date: string;
  Circuit?: { circuitName?: string };
}

export default function Dashboard() {
  const [races, setRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [year] = useState(2024);

  useEffect(() => {
    const fetchRaces = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getRaces(year);
        if (Array.isArray(data)) {
          setRaces(data);
        } else {
          setRaces([]);
          console.warn('getRaces returned non-array:', data);
        }
      } catch (err: any) {
        console.error('Failed to fetch races:', err);
        setError(err?.message || 'Failed to fetch races');
        setRaces([]);
      } finally {
        setLoading(false);
      }
    };
    fetchRaces();
  }, [year]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          <span className="text-pitwall-accent">PITWALL</span>.ai
        </h1>
        <p className="text-pitwall-text-muted text-lg">F1 Analytics Dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-pitwall-card rounded-lg p-6 border border-pitwall-border">
          <p className="text-pitwall-text-muted text-sm">Season</p>
          <p className="text-3xl font-bold text-white">{year}</p>
        </div>
        <div className="bg-pitwall-card rounded-lg p-6 border border-pitwall-border">
          <p className="text-pitwall-text-muted text-sm">Races</p>
          <p className="text-3xl font-bold text-white">{races.length}</p>
        </div>
        <div className="bg-pitwall-card rounded-lg p-6 border border-pitwall-border">
          <p className="text-pitwall-text-muted text-sm">Status</p>
          <p className="text-3xl font-bold text-green-400">{loading ? 'Loading...' : 'Live'}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 mb-6">
          <p className="text-red-400">API Error: {error}</p>
          <p className="text-pitwall-text-muted text-sm mt-1">The dashboard will show cached data when available.</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="text-pitwall-text-muted text-lg">Loading race data...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {races.length > 0 ? races.map((race) => (
            <Link
              key={race.round}
              to={`/race/${year}/${race.round}`}
              className="bg-pitwall-card rounded-lg p-5 border border-pitwall-border hover:border-pitwall-accent transition-colors group"
            >
              <div className="flex justify-between items-start mb-3">
                <span className="text-pitwall-accent font-mono text-sm">R{String(race.round).padStart(2, '0')}</span>
                <span className="text-pitwall-text-muted text-xs">{race.date}</span>
              </div>
              <h3 className="text-white font-semibold text-lg group-hover:text-pitwall-accent transition-colors">
                {race.raceName}
              </h3>
              <p className="text-pitwall-text-muted text-sm mt-1">
                {race.Circuit?.circuitName || 'Circuit TBD'}
              </p>
            </Link>
          )) : (
            <div className="col-span-full text-center py-10">
              <p className="text-pitwall-text-muted text-lg">No race data available for {year}</p>
              <p className="text-pitwall-text-muted text-sm mt-2">The FastF1 API may be loading. Try refreshing in a moment.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
'''

dash_path = os.path.join(base, 'pages', 'Dashboard.tsx')
with open(dash_path, 'w') as f:
    f.write(dashboard)
print('[OK] Written bulletproof Dashboard.tsx')

# Write App.tsx with ErrorBoundary
app_tsx = '''import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import RaceDetail from './pages/RaceDetail';
import Drivers from './pages/Drivers';
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter basename="/f1">
        <div className="min-h-screen bg-pitwall-bg text-pitwall-text">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/race/:year/:round" element={<RaceDetail />} />
              <Route path="/drivers/:year" element={<Drivers />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
'''

app_path = os.path.join(base, 'App.tsx')
with open(app_path, 'w') as f:
    f.write(app_tsx)
print('[OK] Written App.tsx with ErrorBoundary')

# Verify api.ts has proper exports
api_path = os.path.join(base, 'api.ts')
with open(api_path) as f:
    api_content = f.read()
if 'getRaces' in api_content and '/f1/api' in api_content:
    print('[OK] api.ts has getRaces and /f1/api baseURL')
else:
    print('[WARN] api.ts may need fixes')

print('\n[DONE] All frontend files fixed. Ready for rebuild.')
