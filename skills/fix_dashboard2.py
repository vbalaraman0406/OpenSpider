import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix Dashboard.tsx
dashboard_path = os.path.join(base, 'frontend', 'src', 'pages', 'Dashboard.tsx')

new_dashboard = """import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRaces } from '../api';

interface Race {
  round: number;
  raceName: string;
  date: string;
  Circuit?: { circuitName?: string; Location?: { country?: string } };
}

export default function Dashboard() {
  const [races, setRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [year, setYear] = useState(2024);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getRaces(year)
      .then((data) => {
        if (Array.isArray(data)) {
          setRaces(data);
        } else {
          setRaces([]);
          setError('No race data available for ' + year);
        }
      })
      .catch((err) => {
        setRaces([]);
        setError('Failed to load race data: ' + (err?.message || 'Unknown error'));
      })
      .finally(() => setLoading(false));
  }, [year]);

  return (
    <div className="min-h-screen bg-pitwall-bg text-white">
      <header className="border-b border-gray-800 bg-pitwall-card">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">
                <span className="text-pitwall-accent">Pitwall</span>.ai
              </h1>
              <p className="text-gray-400 mt-1">F1 Analytics & Race Intelligence</p>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/drivers/2024" className="px-4 py-2 bg-pitwall-card border border-gray-700 rounded-lg hover:border-pitwall-accent transition-colors">
                Drivers
              </Link>
              <Link to="/compare" className="px-4 py-2 bg-pitwall-card border border-gray-700 rounded-lg hover:border-pitwall-accent transition-colors">
                Compare
              </Link>
            </div>
          </div>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-pitwall-accent/20 to-transparent border border-pitwall-accent/30 rounded-2xl p-8 mb-8">
          <h2 className="text-4xl font-bold mb-4">Welcome to Pitwall.ai</h2>
          <p className="text-xl text-gray-300 mb-6">
            Real-time F1 analytics powered by FastF1. Track metrics, driver stats, and race predictions.
          </p>
          <div className="flex gap-4">
            <span className="px-3 py-1 bg-pitwall-accent/20 text-pitwall-accent rounded-full text-sm">Telemetry</span>
            <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">Race Data</span>
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">Predictions</span>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-8">
          <h3 className="text-xl font-semibold">Race Calendar</h3>
          <div className="flex gap-2">
            {[2024, 2023].map((y) => (
              <button
                key={y}
                onClick={() => setYear(y)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  year === y
                    ? 'bg-pitwall-accent text-white'
                    : 'bg-pitwall-card border border-gray-700 hover:border-pitwall-accent'
                }`}
              >
                {y}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-pitwall-accent"></div>
            <span className="ml-4 text-gray-400">Loading race data...</span>
          </div>
        ) : error ? (
          <div className="bg-pitwall-card border border-yellow-600/30 rounded-xl p-8 text-center">
            <p className="text-yellow-400 text-lg mb-2">{error}</p>
            <p className="text-gray-400">FastF1 data pipeline is being configured. Check back soon!</p>
          </div>
        ) : races.length === 0 ? (
          <div className="bg-pitwall-card border border-gray-700 rounded-xl p-8 text-center">
            <p className="text-gray-400 text-lg">No races found for {year}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {races.map((race) => (
              <Link
                key={race.round}
                to={`/race/${year}/${race.round}`}
                className="bg-pitwall-card border border-gray-700 rounded-xl p-6 hover:border-pitwall-accent transition-all hover:shadow-lg hover:shadow-pitwall-accent/10"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-pitwall-accent font-mono text-sm">R{String(race.round).padStart(2, '0')}</span>
                  <span className="text-gray-500 text-sm">{race.date}</span>
                </div>
                <h4 className="text-lg font-semibold mb-1">{race.raceName}</h4>
                <p className="text-gray-400 text-sm">
                  {race.Circuit?.circuitName || 'Circuit TBD'}
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>

      <footer className="border-t border-gray-800 mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          Pitwall.ai 2026 | Powered by FastF1 & FastAPI
        </div>
      </footer>
    </div>
  );
}
"""

with open(dashboard_path, 'w') as f:
    f.write(new_dashboard)
print(f'Dashboard.tsx updated: {os.path.getsize(dashboard_path)} bytes')

# Fix api.ts
api_path = os.path.join(base, 'frontend', 'src', 'api.ts')

new_api = """import axios from 'axios';

const api = axios.create({
  baseURL: '/f1/api',
  timeout: 30000,
});

export const getRaces = async (year: number) => {
  try {
    const res = await api.get(`/races/${year}`);
    return res.data;
  } catch (err) {
    console.error('getRaces error:', err);
    return [];
  }
};

export const getRaceResults = async (year: number, round: number) => {
  try {
    const res = await api.get(`/race/${year}/${round}/results`);
    return res.data;
  } catch (err) {
    console.error('getRaceResults error:', err);
    return [];
  }
};

export const getRaceLaps = async (year: number, round: number) => {
  try {
    const res = await api.get(`/race/${year}/${round}/laps`);
    return res.data;
  } catch (err) {
    console.error('getRaceLaps error:', err);
    return [];
  }
};

export const getDrivers = async (year: number) => {
  try {
    const res = await api.get(`/drivers/${year}`);
    return res.data;
  } catch (err) {
    console.error('getDrivers error:', err);
    return [];
  }
};

export const getDriverStats = async (driverId: string, year: number) => {
  try {
    const res = await api.get(`/driver/${driverId}/${year}/stats`);
    return res.data;
  } catch (err) {
    console.error('getDriverStats error:', err);
    return null;
  }
};

export default api;
"""

with open(api_path, 'w') as f:
    f.write(new_api)
print(f'api.ts updated: {os.path.getsize(api_path)} bytes')
print('Done. Ready to rebuild frontend.')
