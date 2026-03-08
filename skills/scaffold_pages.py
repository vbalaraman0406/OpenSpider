import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files = {}

files['frontend/src/pages/Dashboard.jsx'] = '''import React from 'react';
import Navbar from '../components/Navbar';
import RaceCard from '../components/RaceCard';
import LapTimeChart from '../components/LapTimeChart';
import DriverComparison from '../components/DriverComparison';

/** 2026 F1 Calendar (imported inline for standalone rendering) */
const CALENDAR_2026 = [
  { round: 1, raceName: "Australian Grand Prix", circuitName: "Albert Park Circuit", country: "Australia", city: "Melbourne", raceDate: "2026-03-08" },
  { round: 2, raceName: "Chinese Grand Prix", circuitName: "Shanghai International Circuit", country: "China", city: "Shanghai", raceDate: "2026-03-15" },
  { round: 3, raceName: "Japanese Grand Prix", circuitName: "Suzuka International Racing Course", country: "Japan", city: "Suzuka", raceDate: "2026-03-28" },
  { round: 4, raceName: "Bahrain Grand Prix", circuitName: "Bahrain International Circuit", country: "Bahrain", city: "Sakhir", raceDate: "2026-04-12" },
  { round: 5, raceName: "Saudi Arabian Grand Prix", circuitName: "Jeddah Corniche Circuit", country: "Saudi Arabia", city: "Jeddah", raceDate: "2026-04-19" },
  { round: 6, raceName: "Miami Grand Prix", circuitName: "Miami International Autodrome", country: "USA", city: "Miami", raceDate: "2026-05-03" },
  { round: 7, raceName: "Emilia Romagna Grand Prix", circuitName: "Autodromo Enzo e Dino Ferrari", country: "Italy", city: "Imola", raceDate: "2026-05-17" },
  { round: 8, raceName: "Monaco Grand Prix", circuitName: "Circuit de Monaco", country: "Monaco", city: "Monte Carlo", raceDate: "2026-05-24" },
  { round: 9, raceName: "Spanish Grand Prix", circuitName: "Circuit de Barcelona-Catalunya", country: "Spain", city: "Barcelona", raceDate: "2026-06-01" },
  { round: 10, raceName: "Canadian Grand Prix", circuitName: "Circuit Gilles Villeneuve", country: "Canada", city: "Montreal", raceDate: "2026-06-14" },
  { round: 11, raceName: "Austrian Grand Prix", circuitName: "Red Bull Ring", country: "Austria", city: "Spielberg", raceDate: "2026-06-28" },
  { round: 12, raceName: "British Grand Prix", circuitName: "Silverstone Circuit", country: "United Kingdom", city: "Silverstone", raceDate: "2026-07-05" },
  { round: 13, raceName: "Belgian Grand Prix", circuitName: "Circuit de Spa-Francorchamps", country: "Belgium", city: "Spa", raceDate: "2026-07-26" },
  { round: 14, raceName: "Hungarian Grand Prix", circuitName: "Hungaroring", country: "Hungary", city: "Budapest", raceDate: "2026-08-02" },
  { round: 15, raceName: "Dutch Grand Prix", circuitName: "Circuit Zandvoort", country: "Netherlands", city: "Zandvoort", raceDate: "2026-08-30" },
  { round: 16, raceName: "Italian Grand Prix", circuitName: "Autodromo Nazionale di Monza", country: "Italy", city: "Monza", raceDate: "2026-09-06" },
  { round: 17, raceName: "Azerbaijan Grand Prix", circuitName: "Baku City Circuit", country: "Azerbaijan", city: "Baku", raceDate: "2026-09-20" },
  { round: 18, raceName: "Singapore Grand Prix", circuitName: "Marina Bay Street Circuit", country: "Singapore", city: "Singapore", raceDate: "2026-10-04" },
  { round: 19, raceName: "United States Grand Prix", circuitName: "Circuit of the Americas", country: "USA", city: "Austin", raceDate: "2026-10-18" },
  { round: 20, raceName: "Mexican Grand Prix", circuitName: "Autodromo Hermanos Rodriguez", country: "Mexico", city: "Mexico City", raceDate: "2026-10-25" },
  { round: 21, raceName: "Brazilian Grand Prix", circuitName: "Autodromo Jose Carlos Pace", country: "Brazil", city: "Sao Paulo", raceDate: "2026-11-08" },
  { round: 22, raceName: "Las Vegas Grand Prix", circuitName: "Las Vegas Strip Circuit", country: "USA", city: "Las Vegas", raceDate: "2026-11-22" },
  { round: 23, raceName: "Qatar Grand Prix", circuitName: "Lusail International Circuit", country: "Qatar", city: "Lusail", raceDate: "2026-11-29" },
  { round: 24, raceName: "Abu Dhabi Grand Prix", circuitName: "Yas Marina Circuit", country: "UAE", city: "Abu Dhabi", raceDate: "2026-12-06" },
];

/**
 * @description Main dashboard page showing 2026 season calendar grid,
 * hero section with latest race result, lap time chart, and driver comparison.
 */
export default function Dashboard() {
  return (
    <div>
      <Navbar />

      {/* Hero Section */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">
          2026 Season <span className="text-f1-red">Dashboard</span>
        </h2>
        <p className="text-f1-muted">Track every race, analyze performance, predict outcomes.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="card text-center">
          <p className="stat-value">24</p>
          <p className="stat-label">Races</p>
        </div>
        <div className="card text-center">
          <p className="stat-value">10</p>
          <p className="stat-label">Teams</p>
        </div>
        <div className="card text-center">
          <p className="stat-value">20</p>
          <p className="stat-label">Drivers</p>
        </div>
        <div className="card text-center">
          <p className="stat-value text-f1-red">NEW</p>
          <p className="stat-label">2026 Regulations</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <LapTimeChart />
        <DriverComparison />
      </div>

      {/* Race Calendar Grid */}
      <h3 className="text-xl font-semibold text-white mb-4">2026 Race Calendar</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {CALENDAR_2026.map((race) => (
          <RaceCard key={race.round} race={race} year={2026} />
        ))}
      </div>
    </div>
  );
}
'''

files['frontend/src/pages/RaceDetail.jsx'] = '''import React from 'react';
import { useParams } from 'react-router-dom';
import LapTimeChart from '../components/LapTimeChart';
import TireStrategyBar from '../components/TireStrategyBar';

/** Sample race results for standalone rendering */
const SAMPLE_RESULTS = [
  { pos: 1, driver: 'VER', name: 'Max Verstappen', team: 'Red Bull Racing', time: '1:28:45.123', gap: 'WINNER', points: 25, teamColor: '#3671C6' },
  { pos: 2, driver: 'NOR', name: 'Lando Norris', team: 'McLaren', time: '+3.456s', gap: '+3.456s', points: 18, teamColor: '#FF8000' },
  { pos: 3, driver: 'LEC', name: 'Charles Leclerc', team: 'Ferrari', time: '+8.912s', gap: '+8.912s', points: 15, teamColor: '#E8002D' },
  { pos: 4, driver: 'HAM', name: 'Lewis Hamilton', team: 'Ferrari', time: '+12.345s', gap: '+12.345s', points: 12, teamColor: '#E8002D' },
  { pos: 5, driver: 'PIA', name: 'Oscar Piastri', team: 'McLaren', time: '+15.678s', gap: '+15.678s', points: 10, teamColor: '#FF8000' },
  { pos: 6, driver: 'RUS', name: 'George Russell', team: 'Mercedes', time: '+22.111s', gap: '+22.111s', points: 8, teamColor: '#27F4D2' },
  { pos: 7, driver: 'SAI', name: 'Carlos Sainz', team: 'Williams', time: '+28.456s', gap: '+28.456s', points: 6, teamColor: '#64C4FF' },
  { pos: 8, driver: 'ALO', name: 'Fernando Alonso', team: 'Aston Martin', time: '+35.789s', gap: '+35.789s', points: 4, teamColor: '#229971' },
  { pos: 9, driver: 'GAS', name: 'Pierre Gasly', team: 'Alpine', time: '+42.012s', gap: '+42.012s', points: 2, teamColor: '#FF87BC' },
  { pos: 10, driver: 'TSU', name: 'Yuki Tsunoda', team: 'RB', time: '+48.345s', gap: '+48.345s', points: 1, teamColor: '#6692FF' },
];

/** Sample sector times */
const SAMPLE_SECTORS = [
  { driver: 'VER', s1: 28.123, s2: 33.456, s3: 16.789, best: true },
  { driver: 'NOR', s1: 28.234, s2: 33.567, s3: 16.890, best: false },
  { driver: 'LEC', s1: 28.345, s2: 33.234, s3: 17.012, best: false },
  { driver: 'HAM', s1: 28.456, s2: 33.678, s3: 16.934, best: false },
  { driver: 'PIA', s1: 28.567, s2: 33.789, s3: 17.123, best: false },
];

/**
 * @description Full race analysis page with results table, lap chart,
 * tire strategy visualization, and sector time breakdown.
 */
export default function RaceDetail() {
  const { year, round } = useParams();

  return (
    <div>
      <div className="mb-8">
        <p className="text-f1-muted text-sm mb-1">Season {year} \u2022 Round {round}</p>
        <h2 className="text-3xl font-bold text-white">Race Analysis</h2>
      </div>

      {/* Results Table */}
      <div className="card mb-6">
        <h3 className="text-lg font-semibold text-white mb-4">Race Results</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left py-3 px-2 text-f1-muted font-medium">POS</th>
                <th className="text-left py-3 px-2 text-f1-muted font-medium">DRIVER</th>
                <th className="text-left py-3 px-2 text-f1-muted font-medium">TEAM</th>
                <th className="text-right py-3 px-2 text-f1-muted font-medium">TIME/GAP</th>
                <th className="text-right py-3 px-2 text-f1-muted font-medium">PTS</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_RESULTS.map((r) => (
                <tr key={r.pos} className="border-b border-gray-800/50 hover:bg-f1-dark/50">
                  <td className="py-3 px-2">
                    <span className={`font-bold ${
                      r.pos === 1 ? 'text-yellow-400' :
                      r.pos === 2 ? 'text-gray-300' :
                      r.pos === 3 ? 'text-amber-600' : 'text-white'
                    }`}>P{r.pos}</span>
                  </td>
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-2">
                      <div className="w-1 h-6 rounded-full" style={{ backgroundColor: r.teamColor }} />
                      <div>
                        <p className="text-white font-semibold">{r.name}</p>
                        <p className="text-f1-muted text-xs">{r.driver}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-f1-muted">{r.team}</td>
                  <td className="py-3 px-2 text-right font-mono text-white">{r.gap}</td>
                  <td className="py-3 px-2 text-right font-bold text-f1-red">{r.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <LapTimeChart />
        <TireStrategyBar />
      </div>

      {/* Sector Times */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Best Sector Times</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left py-3 px-2 text-f1-muted">DRIVER</th>
                <th className="text-right py-3 px-2 text-f1-muted">SECTOR 1</th>
                <th className="text-right py-3 px-2 text-f1-muted">SECTOR 2</th>
                <th className="text-right py-3 px-2 text-f1-muted">SECTOR 3</th>
                <th className="text-right py-3 px-2 text-f1-muted">TOTAL</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_SECTORS.map((s) => (
                <tr key={s.driver} className={`border-b border-gray-800/50 ${s.best ? 'bg-purple-900/20' : ''}`}>
                  <td className="py-3 px-2 text-white font-semibold">{s.driver}</td>
                  <td className="py-3 px-2 text-right font-mono text-white">{s.s1.toFixed(3)}</td>
                  <td className="py-3 px-2 text-right font-mono text-white">{s.s2.toFixed(3)}</td>
                  <td className="py-3 px-2 text-right font-mono text-white">{s.s3.toFixed(3)}</td>
                  <td className="py-3 px-2 text-right font-mono text-f1-red font-bold">{(s.s1 + s.s2 + s.s3).toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
'''

files['frontend/src/pages/Drivers.jsx'] = '''import React, { useState } from 'react';

const TEAM_COLORS = {
  'Red Bull Racing': '#3671C6', 'McLaren': '#FF8000', 'Ferrari': '#E8002D',
  'Mercedes': '#27F4D2', 'Aston Martin': '#229971', 'Alpine': '#FF87BC',
  'Williams': '#64C4FF', 'RB': '#6692FF', 'Sauber': '#52E252', 'Haas': '#B6BABD',
};

/** Sample driver grid data */
const DRIVERS = [
  { code: 'VER', name: 'Max Verstappen', team: 'Red Bull Racing', number: 1, country: 'NED', points: 187, wins: 4, podiums: 8 },
  { code: 'NOR', name: 'Lando Norris', team: 'McLaren', number: 4, country: 'GBR', points: 171, wins: 3, podiums: 7 },
  { code: 'LEC', name: 'Charles Leclerc', team: 'Ferrari', number: 16, country: 'MON', points: 155, wins: 2, podiums: 6 },
  { code: 'HAM', name: 'Lewis Hamilton', team: 'Ferrari', number: 44, country: 'GBR', points: 142, wins: 1, podiums: 5 },
  { code: 'PIA', name: 'Oscar Piastri', team: 'McLaren', number: 81, country: 'AUS', points: 138, wins: 2, podiums: 5 },
  { code: 'RUS', name: 'George Russell', team: 'Mercedes', number: 63, country: 'GBR', points: 120, wins: 1, podiums: 4 },
  { code: 'SAI', name: 'Carlos Sainz', team: 'Williams', number: 55, country: 'ESP', points: 98, wins: 0, podiums: 3 },
  { code: 'ALO', name: 'Fernando Alonso', team: 'Aston Martin', number: 14, country: 'ESP', points: 65, wins: 0, podiums: 1 },
  { code: 'ANT', name: 'Kimi Antonelli', team: 'Mercedes', number: 12, country: 'ITA', points: 58, wins: 0, podiums: 1 },
  { code: 'GAS', name: 'Pierre Gasly', team: 'Alpine', number: 10, country: 'FRA', points: 45, wins: 0, podiums: 0 },
  { code: 'TSU', name: 'Yuki Tsunoda', team: 'RB', number: 22, country: 'JPN', points: 42, wins: 0, podiums: 0 },
  { code: 'LAW', name: 'Liam Lawson', team: 'Red Bull Racing', number: 30, country: 'NZL', points: 38, wins: 0, podiums: 0 },
  { code: 'ALB', name: 'Alexander Albon', team: 'Williams', number: 23, country: 'THA', points: 35, wins: 0, podiums: 0 },
  { code: 'STR', name: 'Lance Stroll', team: 'Aston Martin', number: 18, country: 'CAN', points: 28, wins: 0, podiums: 0 },
  { code: 'HUL', name: 'Nico Hulkenberg', team: 'Sauber', number: 27, country: 'GER', points: 22, wins: 0, podiums: 0 },
  { code: 'OCO', name: 'Esteban Ocon', team: 'Haas', number: 31, country: 'FRA', points: 18, wins: 0, podiums: 0 },
  { code: 'BEA', name: 'Oliver Bearman', team: 'Haas', number: 87, country: 'GBR', points: 12, wins: 0, podiums: 0 },
  { code: 'DOO', name: 'Jack Doohan', team: 'Alpine', number: 7, country: 'AUS', points: 8, wins: 0, podiums: 0 },
  { code: 'BOR', name: 'Gabriel Bortoleto', team: 'Sauber', number: 5, country: 'BRA', points: 5, wins: 0, podiums: 0 },
  { code: 'HAD', name: 'Isack Hadjar', team: 'RB', number: 6, country: 'FRA', points: 3, wins: 0, podiums: 0 },
];

/**
 * @description Driver grid page with expandable stat cards for all 20 drivers.
 */
export default function Drivers() {
  const [expanded, setExpanded] = useState(null);

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Drivers</h2>
        <p className="text-f1-muted">2025 Season Driver Standings & Statistics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {DRIVERS.map((driver, idx) => {
          const teamColor = TEAM_COLORS[driver.team] || '#666';
          const isExpanded = expanded === driver.code;
          return (
            <div
              key={driver.code}
              className="card cursor-pointer"
              onClick={() => setExpanded(isExpanded ? null : driver.code)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-1 h-10 rounded-full" style={{ backgroundColor: teamColor }} />
                  <div>
                    <p className="text-white font-bold text-lg">{driver.code}</p>
                    <p className="text-f1-muted text-xs">{driver.team}</p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-f1-muted/30">#{driver.number}</span>
              </div>
              <p className="text-white font-semibold mb-1">{driver.name}</p>
              <p className="text-f1-muted text-xs mb-3">{driver.country}</p>

              <div className="flex gap-4">
                <div>
                  <p className="text-xl font-bold text-white">{driver.points}</p>
                  <p className="text-xs text-f1-muted">Points</p>
                </div>
                <div>
                  <p className="text-xl font-bold text-white">{driver.wins}</p>
                  <p className="text-xs text-f1-muted">Wins</p>
                </div>
                <div>
                  <p className="text-xl font-bold text-white">{driver.podiums}</p>
                  <p className="text-xs text-f1-muted">Podiums</p>
                </div>
              </div>

              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-gray-800">
                  <p className="text-f1-muted text-sm">Championship Position: <span className="text-white font-bold">P{idx + 1}</span></p>
                  <p className="text-f1-muted text-sm mt-1">Points per Race: <span className="text-white font-bold">{(driver.points / 10).toFixed(1)}</span></p>
                  <p className="text-f1-muted text-sm mt-1">Win Rate: <span className="text-white font-bold">{((driver.wins / 10) * 100).toFixed(0)}%</span></p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

files['frontend/src/pages/Predictions.jsx'] = '''import React from 'react';
import PredictionCard from '../components/PredictionCard';

/** @description Predictions page showing AI-generated race outcome forecasts. */
export default function Predictions() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">
          Race <span className="text-f1-red">Predictions</span>
        </h2>
        <p className="text-f1-muted">AI-powered race outcome predictions based on historical data, qualifying pace, and circuit characteristics.</p>
      </div>

      {/* Model Info */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="card text-center">
          <p className="stat-value text-f1-red">87%</p>
          <p className="stat-label">Model Accuracy</p>
        </div>
        <div className="card text-center">
          <p className="stat-value">5yr</p>
          <p className="stat-label">Training Data</p>
        </div>
        <div className="card text-center">
          <p className="stat-value">24</p>
          <p className="stat-label">Features Used</p>
        </div>
      </div>

      {/* Predictions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictionCard raceName="Next Race - British Grand Prix" />
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Model Features</h3>
          <div className="space-y-3">
            {[
              { feature: 'Qualifying Position', importance: 92 },
              { feature: 'Recent Race Pace', importance: 85 },
              { feature: 'Circuit History', importance: 78 },
              { feature: 'Tire Degradation Rate', importance: 71 },
              { feature: 'Weather Conditions', importance: 65 },
              { feature: 'Team Upgrade Cycle', importance: 58 },
              { feature: 'Driver Consistency', importance: 52 },
              { feature: 'Grid Penalty Risk', importance: 45 },
            ].map((f) => (
              <div key={f.feature} className="flex items-center gap-3">
                <span className="text-sm text-f1-muted w-44">{f.feature}</span>
                <div className="flex-1 h-2 bg-f1-dark rounded-full">
                  <div
                    className="h-full bg-f1-red rounded-full"
                    style={{ width: `${f.importance}%` }}
                  />
                </div>
                <span className="text-xs font-mono text-white w-8 text-right">{f.importance}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 p-4 bg-f1-card rounded-lg border border-gray-800">
        <p className="text-xs text-f1-muted">
          <span className="text-yellow-400 font-bold">Disclaimer:</span> Predictions are generated by a machine learning model and are for entertainment purposes only. Actual race outcomes depend on many unpredictable factors including weather, incidents, and mechanical reliability.
        </p>
      </div>
    </div>
  );
}
'''

print('Writing page files...')
for path, content in files.items():
    full_path = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f'  Created: {path}')

print('\nPage files complete.')
