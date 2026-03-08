import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files = {}

# src/components/Layout.jsx
files['frontend/src/components/Layout.jsx'] = '''import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: '\u2302' },
  { path: '/drivers', label: 'Drivers', icon: '\u2691' },
  { path: '/predictions', label: 'Predictions', icon: '\u2604' },
];

/**
 * @description Main layout with dark sidebar navigation and content area.
 * Includes Pitwall.ai branding and responsive sidebar.
 */
export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-f1-card border-r border-gray-800 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-f1-red rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">Pitwall<span className="text-f1-red">.ai</span></h1>
              <p className="text-xs text-f1-muted">F1 Analytics</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-f1-red/10 text-f1-red border border-f1-red/20'
                    : 'text-f1-muted hover:text-white hover:bg-f1-card-hover'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <div className="text-xs text-f1-muted">
            <p>Powered by FastF1</p>
            <p className="mt-1">v1.0.0</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-f1-dark">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
'''

# src/components/Navbar.jsx
files['frontend/src/components/Navbar.jsx'] = '''import React, { useState, useEffect } from 'react';

/** @description Top navigation bar with next race countdown timer. */
export default function Navbar() {
  const [countdown, setCountdown] = useState('');

  useEffect(() => {
    const nextRace = new Date('2025-07-06T14:00:00Z'); // British GP 2025
    const raceName = 'British Grand Prix';

    const timer = setInterval(() => {
      const now = new Date();
      const diff = nextRace - now;
      if (diff <= 0) {
        setCountdown('Race in progress!');
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const secs = Math.floor((diff % (1000 * 60)) / 1000);
      setCountdown(`${raceName}: ${days}d ${hours}h ${mins}m ${secs}s`);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center justify-between mb-8">
      <div />
      <div className="bg-f1-card border border-gray-800 rounded-lg px-4 py-2">
        <span className="text-xs text-f1-muted mr-2">NEXT RACE</span>
        <span className="text-sm font-mono text-white">{countdown}</span>
      </div>
    </div>
  );
}
'''

# src/components/RaceCard.jsx
files['frontend/src/components/RaceCard.jsx'] = '''import React from 'react';
import { Link } from 'react-router-dom';

const COUNTRY_FLAGS = {
  'Australia': '\U0001f1e6\U0001f1fa', 'China': '\U0001f1e8\U0001f1f3', 'Japan': '\U0001f1ef\U0001f1f5',
  'Bahrain': '\U0001f1e7\U0001f1ed', 'Saudi Arabia': '\U0001f1f8\U0001f1e6', 'USA': '\U0001f1fa\U0001f1f8',
  'Italy': '\U0001f1ee\U0001f1f9', 'Monaco': '\U0001f1f2\U0001f1e8', 'Spain': '\U0001f1ea\U0001f1f8',
  'Canada': '\U0001f1e8\U0001f1e6', 'Austria': '\U0001f1e6\U0001f1f9', 'United Kingdom': '\U0001f1ec\U0001f1e7',
  'Belgium': '\U0001f1e7\U0001f1ea', 'Hungary': '\U0001f1ed\U0001f1fa', 'Netherlands': '\U0001f1f3\U0001f1f1',
  'Azerbaijan': '\U0001f1e6\U0001f1ff', 'Singapore': '\U0001f1f8\U0001f1ec', 'Mexico': '\U0001f1f2\U0001f1fd',
  'Brazil': '\U0001f1e7\U0001f1f7', 'Qatar': '\U0001f1f6\U0001f1e6', 'UAE': '\U0001f1e6\U0001f1ea',
};

/**
 * @description Card component displaying race info with country flag,
 * circuit name, date, and link to race detail page.
 * @param {Object} props
 * @param {Object} props.race - Race data object
 * @param {number} props.year - Season year
 */
export default function RaceCard({ race, year = 2026 }) {
  const flag = COUNTRY_FLAGS[race.country] || '\U0001f3c1';
  const date = new Date(race.raceDate);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return (
    <Link to={`/race/${year}/${race.round}`} className="card block group cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <span className="text-3xl">{flag}</span>
        <span className="text-xs font-mono text-f1-muted bg-f1-dark px-2 py-1 rounded">
          R{String(race.round).padStart(2, '0')}
        </span>
      </div>
      <h3 className="text-white font-semibold text-lg mb-1 group-hover:text-f1-red transition-colors">
        {race.raceName}
      </h3>
      <p className="text-f1-muted text-sm mb-2">{race.circuitName}</p>
      <div className="flex items-center justify-between">
        <span className="text-f1-muted text-xs">{race.city}, {race.country}</span>
        <span className="text-f1-red text-sm font-semibold">{dateStr}</span>
      </div>
    </Link>
  );
}
'''

# src/components/LapTimeChart.jsx
files['frontend/src/components/LapTimeChart.jsx'] = '''import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/** Sample lap time data for demo rendering */
const SAMPLE_DATA = Array.from({ length: 57 }, (_, i) => ({
  lap: i + 1,
  VER: 78.5 + Math.random() * 2 + (i === 20 || i === 40 ? 15 : 0),
  NOR: 78.8 + Math.random() * 2 + (i === 22 || i === 42 ? 15 : 0),
  LEC: 79.0 + Math.random() * 2 + (i === 18 || i === 38 ? 15 : 0),
}));

const DRIVER_COLORS = {
  VER: '#3671C6', NOR: '#FF8000', LEC: '#E8002D',
  HAM: '#E8002D', RUS: '#27F4D2', PIA: '#FF8000',
  SAI: '#64C4FF', ALO: '#229971', STR: '#229971',
};

/**
 * @description Recharts line chart displaying lap times for multiple drivers.
 * @param {Object} props
 * @param {Array} props.data - Array of lap time objects
 * @param {Array} props.drivers - Array of driver abbreviations to display
 */
export default function LapTimeChart({ data = SAMPLE_DATA, drivers = ['VER', 'NOR', 'LEC'] }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Lap Times</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="lap" stroke="#6B7280" tick={{ fontSize: 11 }} label={{ value: 'Lap', position: 'insideBottom', offset: -5, fill: '#6B7280' }} />
          <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} domain={['auto', 'auto']} label={{ value: 'Time (s)', angle: -90, position: 'insideLeft', fill: '#6B7280' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1E1E2E', border: '1px solid #333', borderRadius: '8px' }}
            labelStyle={{ color: '#9CA3AF' }}
          />
          <Legend />
          {drivers.map((driver) => (
            <Line
              key={driver}
              type="monotone"
              dataKey={driver}
              stroke={DRIVER_COLORS[driver] || '#FFFFFF'}
              dot={false}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
'''

# src/components/TireStrategyBar.jsx
files['frontend/src/components/TireStrategyBar.jsx'] = '''import React from 'react';

const COMPOUND_COLORS = {
  SOFT: '#FF3333',
  MEDIUM: '#FFD700',
  HARD: '#FFFFFF',
  INTERMEDIATE: '#39B54A',
  WET: '#0067FF',
};

/** Sample tire strategy data */
const SAMPLE_STRATEGIES = [
  { driver: 'VER', stints: [{ compound: 'SOFT', laps: 18 }, { compound: 'HARD', laps: 22 }, { compound: 'MEDIUM', laps: 17 }] },
  { driver: 'NOR', stints: [{ compound: 'MEDIUM', laps: 22 }, { compound: 'HARD', laps: 20 }, { compound: 'SOFT', laps: 15 }] },
  { driver: 'LEC', stints: [{ compound: 'SOFT', laps: 15 }, { compound: 'MEDIUM', laps: 25 }, { compound: 'HARD', laps: 17 }] },
  { driver: 'HAM', stints: [{ compound: 'MEDIUM', laps: 20 }, { compound: 'HARD', laps: 25 }, { compound: 'SOFT', laps: 12 }] },
  { driver: 'PIA', stints: [{ compound: 'SOFT', laps: 16 }, { compound: 'HARD', laps: 28 }, { compound: 'MEDIUM', laps: 13 }] },
];

/**
 * @description Horizontal stacked bar chart showing tire compounds per stint.
 * @param {Object} props
 * @param {Array} props.strategies - Array of driver strategy objects
 */
export default function TireStrategyBar({ strategies = SAMPLE_STRATEGIES }) {
  const maxLaps = Math.max(...strategies.map(s => s.stints.reduce((sum, st) => sum + st.laps, 0)));

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Tire Strategy</h3>
      <div className="space-y-3">
        {strategies.map((strategy) => {
          const totalLaps = strategy.stints.reduce((sum, st) => sum + st.laps, 0);
          return (
            <div key={strategy.driver} className="flex items-center gap-3">
              <span className="text-sm font-mono text-f1-muted w-10">{strategy.driver}</span>
              <div className="flex-1 flex h-7 rounded overflow-hidden">
                {strategy.stints.map((stint, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-center text-xs font-bold"
                    style={{
                      width: `${(stint.laps / maxLaps) * 100}%`,
                      backgroundColor: COMPOUND_COLORS[stint.compound] || '#666',
                      color: stint.compound === 'HARD' || stint.compound === 'MEDIUM' ? '#000' : '#FFF',
                    }}
                    title={`${stint.compound}: ${stint.laps} laps`}
                  >
                    {stint.laps}
                  </div>
                ))}
              </div>
              <span className="text-xs text-f1-muted w-8 text-right">{totalLaps}L</span>
            </div>
          );
        })}
      </div>
      {/* Legend */}
      <div className="flex gap-4 mt-4 pt-3 border-t border-gray-800">
        {Object.entries(COMPOUND_COLORS).map(([compound, color]) => (
          <div key={compound} className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-f1-muted">{compound}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
'''

# src/components/DriverComparison.jsx
files['frontend/src/components/DriverComparison.jsx'] = '''import React from 'react';

/** Sample driver comparison data */
const SAMPLE_DRIVERS = {
  driver1: {
    name: 'Max Verstappen', code: 'VER', team: 'Red Bull Racing', teamColor: '#3671C6',
    stats: { wins: 4, podiums: 8, poles: 5, fastestLaps: 3, points: 187, avgFinish: 2.1 },
  },
  driver2: {
    name: 'Lando Norris', code: 'NOR', team: 'McLaren', teamColor: '#FF8000',
    stats: { wins: 3, podiums: 7, poles: 3, fastestLaps: 2, points: 171, avgFinish: 2.8 },
  },
};

/**
 * @description Side-by-side driver stat comparison component.
 * @param {Object} props
 * @param {Object} props.driver1 - First driver data
 * @param {Object} props.driver2 - Second driver data
 */
export default function DriverComparison({ driver1 = SAMPLE_DRIVERS.driver1, driver2 = SAMPLE_DRIVERS.driver2 }) {
  const statKeys = [
    { key: 'wins', label: 'Wins' },
    { key: 'podiums', label: 'Podiums' },
    { key: 'poles', label: 'Poles' },
    { key: 'fastestLaps', label: 'Fastest Laps' },
    { key: 'points', label: 'Points' },
    { key: 'avgFinish', label: 'Avg Finish', lower: true },
  ];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-6">Driver Comparison</h3>
      {/* Headers */}
      <div className="flex items-center justify-between mb-6">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center text-2xl font-bold" style={{ backgroundColor: driver1.teamColor + '33', color: driver1.teamColor }}>
            {driver1.code}
          </div>
          <p className="text-white font-semibold">{driver1.name}</p>
          <p className="text-f1-muted text-xs">{driver1.team}</p>
        </div>
        <span className="text-f1-muted text-2xl font-bold">VS</span>
        <div className="text-center">
          <div className="w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center text-2xl font-bold" style={{ backgroundColor: driver2.teamColor + '33', color: driver2.teamColor }}>
            {driver2.code}
          </div>
          <p className="text-white font-semibold">{driver2.name}</p>
          <p className="text-f1-muted text-xs">{driver2.team}</p>
        </div>
      </div>
      {/* Stats */}
      <div className="space-y-3">
        {statKeys.map(({ key, label, lower }) => {
          const v1 = driver1.stats[key];
          const v2 = driver2.stats[key];
          const winner1 = lower ? v1 < v2 : v1 > v2;
          const winner2 = lower ? v2 < v1 : v2 > v1;
          return (
            <div key={key} className="flex items-center justify-between py-2 border-b border-gray-800">
              <span className={`text-sm font-mono w-16 text-right ${winner1 ? 'text-green-400 font-bold' : 'text-f1-muted'}`}>{v1}</span>
              <span className="text-xs text-f1-muted uppercase tracking-wider">{label}</span>
              <span className={`text-sm font-mono w-16 ${winner2 ? 'text-green-400 font-bold' : 'text-f1-muted'}`}>{v2}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

# src/components/PredictionCard.jsx
files['frontend/src/components/PredictionCard.jsx'] = '''import React from 'react';

const TEAM_COLORS = {
  'Red Bull Racing': '#3671C6', 'McLaren': '#FF8000', 'Ferrari': '#E8002D',
  'Mercedes': '#27F4D2', 'Aston Martin': '#229971', 'Alpine': '#FF87BC',
  'Williams': '#64C4FF', 'RB': '#6692FF', 'Sauber': '#52E252',
  'Haas': '#B6BABD',
};

/** Sample prediction data */
const SAMPLE_PREDICTIONS = [
  { position: 1, driver: 'VER', name: 'Max Verstappen', team: 'Red Bull Racing', confidence: 89.2 },
  { position: 2, driver: 'NOR', name: 'Lando Norris', team: 'McLaren', confidence: 85.7 },
  { position: 3, driver: 'LEC', name: 'Charles Leclerc', team: 'Ferrari', confidence: 82.1 },
  { position: 4, driver: 'HAM', name: 'Lewis Hamilton', team: 'Ferrari', confidence: 79.5 },
  { position: 5, driver: 'PIA', name: 'Oscar Piastri', team: 'McLaren', confidence: 76.3 },
  { position: 6, driver: 'RUS', name: 'George Russell', team: 'Mercedes', confidence: 73.8 },
  { position: 7, driver: 'SAI', name: 'Carlos Sainz', team: 'Williams', confidence: 70.2 },
  { position: 8, driver: 'ALO', name: 'Fernando Alonso', team: 'Aston Martin', confidence: 67.9 },
  { position: 9, driver: 'GAS', name: 'Pierre Gasly', team: 'Alpine', confidence: 64.1 },
  { position: 10, driver: 'TSU', name: 'Yuki Tsunoda', team: 'RB', confidence: 61.5 },
];

/**
 * @description Predicted finishing order card with confidence percentages.
 * @param {Object} props
 * @param {Array} props.predictions - Array of prediction objects
 * @param {string} props.raceName - Name of the race
 */
export default function PredictionCard({ predictions = SAMPLE_PREDICTIONS, raceName = 'Next Race' }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Predicted Order</h3>
        <span className="text-xs text-f1-muted bg-f1-dark px-2 py-1 rounded">AI Model v1.0</span>
      </div>
      <div className="space-y-2">
        {predictions.map((pred) => {
          const teamColor = TEAM_COLORS[pred.team] || '#666';
          return (
            <div key={pred.driver} className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-f1-dark/50 transition-colors">
              <span className={`text-lg font-bold w-8 text-center ${
                pred.position === 1 ? 'text-yellow-400' :
                pred.position === 2 ? 'text-gray-300' :
                pred.position === 3 ? 'text-amber-600' : 'text-f1-muted'
              }`}>
                P{pred.position}
              </span>
              <div className="w-1 h-8 rounded-full" style={{ backgroundColor: teamColor }} />
              <div className="flex-1">
                <p className="text-white text-sm font-semibold">{pred.name}</p>
                <p className="text-f1-muted text-xs">{pred.team}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-mono text-white">{pred.confidence}%</span>
                <div className="w-20 h-1.5 bg-f1-dark rounded-full mt-1">
                  <div className="h-full rounded-full" style={{ width: `${pred.confidence}%`, backgroundColor: teamColor }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

print('Writing component files...')
for path, content in files.items():
    full_path = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f'  Created: {path}')

print('\nComponent files complete.')
