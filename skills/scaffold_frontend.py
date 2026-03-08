import os
import json

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files = {}

# 2026 Calendar JSON
calendar = [
    {"round": 1, "raceName": "Australian Grand Prix", "circuitName": "Albert Park Circuit", "country": "Australia", "city": "Melbourne", "raceDate": "2026-03-08"},
    {"round": 2, "raceName": "Chinese Grand Prix", "circuitName": "Shanghai International Circuit", "country": "China", "city": "Shanghai", "raceDate": "2026-03-15"},
    {"round": 3, "raceName": "Japanese Grand Prix", "circuitName": "Suzuka International Racing Course", "country": "Japan", "city": "Suzuka", "raceDate": "2026-03-28"},
    {"round": 4, "raceName": "Bahrain Grand Prix", "circuitName": "Bahrain International Circuit", "country": "Bahrain", "city": "Sakhir", "raceDate": "2026-04-12"},
    {"round": 5, "raceName": "Saudi Arabian Grand Prix", "circuitName": "Jeddah Corniche Circuit", "country": "Saudi Arabia", "city": "Jeddah", "raceDate": "2026-04-19"},
    {"round": 6, "raceName": "Miami Grand Prix", "circuitName": "Miami International Autodrome", "country": "USA", "city": "Miami", "raceDate": "2026-05-03"},
    {"round": 7, "raceName": "Emilia Romagna Grand Prix", "circuitName": "Autodromo Enzo e Dino Ferrari", "country": "Italy", "city": "Imola", "raceDate": "2026-05-17"},
    {"round": 8, "raceName": "Monaco Grand Prix", "circuitName": "Circuit de Monaco", "country": "Monaco", "city": "Monte Carlo", "raceDate": "2026-05-24"},
    {"round": 9, "raceName": "Spanish Grand Prix", "circuitName": "Circuit de Barcelona-Catalunya", "country": "Spain", "city": "Barcelona", "raceDate": "2026-06-01"},
    {"round": 10, "raceName": "Canadian Grand Prix", "circuitName": "Circuit Gilles Villeneuve", "country": "Canada", "city": "Montreal", "raceDate": "2026-06-14"},
    {"round": 11, "raceName": "Austrian Grand Prix", "circuitName": "Red Bull Ring", "country": "Austria", "city": "Spielberg", "raceDate": "2026-06-28"},
    {"round": 12, "raceName": "British Grand Prix", "circuitName": "Silverstone Circuit", "country": "United Kingdom", "city": "Silverstone", "raceDate": "2026-07-05"},
    {"round": 13, "raceName": "Belgian Grand Prix", "circuitName": "Circuit de Spa-Francorchamps", "country": "Belgium", "city": "Spa", "raceDate": "2026-07-26"},
    {"round": 14, "raceName": "Hungarian Grand Prix", "circuitName": "Hungaroring", "country": "Hungary", "city": "Budapest", "raceDate": "2026-08-02"},
    {"round": 15, "raceName": "Dutch Grand Prix", "circuitName": "Circuit Zandvoort", "country": "Netherlands", "city": "Zandvoort", "raceDate": "2026-08-30"},
    {"round": 16, "raceName": "Italian Grand Prix", "circuitName": "Autodromo Nazionale di Monza", "country": "Italy", "city": "Monza", "raceDate": "2026-09-06"},
    {"round": 17, "raceName": "Azerbaijan Grand Prix", "circuitName": "Baku City Circuit", "country": "Azerbaijan", "city": "Baku", "raceDate": "2026-09-20"},
    {"round": 18, "raceName": "Singapore Grand Prix", "circuitName": "Marina Bay Street Circuit", "country": "Singapore", "city": "Singapore", "raceDate": "2026-10-04"},
    {"round": 19, "raceName": "United States Grand Prix", "circuitName": "Circuit of the Americas", "country": "USA", "city": "Austin", "raceDate": "2026-10-18"},
    {"round": 20, "raceName": "Mexican Grand Prix", "circuitName": "Autodromo Hermanos Rodriguez", "country": "Mexico", "city": "Mexico City", "raceDate": "2026-10-25"},
    {"round": 21, "raceName": "Brazilian Grand Prix", "circuitName": "Autodromo Jose Carlos Pace", "country": "Brazil", "city": "Sao Paulo", "raceDate": "2026-11-08"},
    {"round": 22, "raceName": "Las Vegas Grand Prix", "circuitName": "Las Vegas Strip Circuit", "country": "USA", "city": "Las Vegas", "raceDate": "2026-11-22"},
    {"round": 23, "raceName": "Qatar Grand Prix", "circuitName": "Lusail International Circuit", "country": "Qatar", "city": "Lusail", "raceDate": "2026-11-29"},
    {"round": 24, "raceName": "Abu Dhabi Grand Prix", "circuitName": "Yas Marina Circuit", "country": "UAE", "city": "Abu Dhabi", "raceDate": "2026-12-06"}
]

with open(os.path.join(BASE, 'f1_2026_calendar.json'), 'w') as f:
    json.dump(calendar, f, indent=2)
print('Created: f1_2026_calendar.json')

# package.json
files['frontend/package.json'] = json.dumps({
    "name": "pitwall-ai-frontend",
    "version": "1.0.0",
    "private": True,
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-router-dom": "^6.20.0",
        "react-scripts": "5.0.1",
        "recharts": "^2.10.0",
        "axios": "^1.6.0",
        "@headlessui/react": "^1.7.17",
        "@heroicons/react": "^2.0.18"
    },
    "devDependencies": {
        "tailwindcss": "^3.3.5",
        "postcss": "^8.4.31",
        "autoprefixer": "^10.4.16"
    },
    "scripts": {
        "start": "react-scripts start",
        "build": "react-scripts build",
        "test": "react-scripts test"
    },
    "browserslist": {
        "production": [">0.2%", "not dead", "not op_mini all"],
        "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
    }
}, indent=2)

# tailwind.config.js
files['frontend/tailwind.config.js'] = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'f1-red': '#E10600',
        'f1-dark': '#15151E',
        'f1-card': '#1E1E2E',
        'f1-card-hover': '#2A2A3E',
        'f1-accent': '#FFFFFF',
        'f1-gray': '#6B7280',
        'f1-muted': '#9CA3AF',
        'tire-soft': '#FF3333',
        'tire-medium': '#FFD700',
        'tire-hard': '#FFFFFF',
        'tire-inter': '#39B54A',
        'tire-wet': '#0067FF',
      },
      fontFamily: {
        'f1': ['Formula1', 'Arial', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
"""

# postcss.config.js
files['frontend/postcss.config.js'] = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
"""

# public/index.html
files['frontend/public/index.html'] = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#15151E" />
    <meta name="description" content="Pitwall.ai - AI-Powered F1 Analytics Platform" />
    <title>Pitwall.ai - F1 Analytics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  </head>
  <body class="bg-f1-dark">
    <noscript>You need to enable JavaScript to run Pitwall.ai.</noscript>
    <div id="root"></div>
  </body>
</html>
"""

# src/index.css
files['frontend/src/index.css'] = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-f1-dark text-white font-sans antialiased;
  }

  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    @apply bg-f1-dark;
  }
  ::-webkit-scrollbar-thumb {
    @apply bg-f1-gray rounded-full;
  }
}

@layer components {
  .card {
    @apply bg-f1-card rounded-xl border border-gray-800 p-6 transition-all duration-200 hover:border-f1-red/30 hover:bg-f1-card-hover;
  }
  .btn-primary {
    @apply bg-f1-red hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200;
  }
  .stat-value {
    @apply text-3xl font-bold text-white tabular-nums;
  }
  .stat-label {
    @apply text-sm text-f1-muted uppercase tracking-wider;
  }
}
"""

# src/index.js
files['frontend/src/index.js'] = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

# src/App.jsx
files['frontend/src/App.jsx'] = """import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RaceDetail from './pages/RaceDetail';
import Drivers from './pages/Drivers';
import Predictions from './pages/Predictions';

/**
 * @description Root application component with routing configuration.
 * Routes: / (Dashboard), /race/:year/:round (Race Detail),
 * /drivers (Driver Stats), /predictions (Predictions)
 */
export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path=\"/\" element={<Dashboard />} />
          <Route path=\"/race/:year/:round\" element={<RaceDetail />} />
          <Route path=\"/drivers\" element={<Drivers />} />
          <Route path=\"/predictions\" element={<Predictions />} />
        </Routes>
      </Layout>
    </Router>
  );
}
"""

# src/services/api.js
files['frontend/src/services/api.js'] = """import axios from 'axios';

/**
 * @description Axios API client for Pitwall.ai backend.
 * All endpoint functions return promises resolving to response data.
 */
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

/** Get season race calendar */
export const getRaces = (year = 2025) => api.get(`/races?year=${year}`).then(r => r.data);

/** Get race detail with results */
export const getRaceDetail = (year, round) => api.get(`/races/${year}/${round}`).then(r => r.data);

/** Get all drivers for a season */
export const getDrivers = (year = 2025) => api.get(`/drivers?year=${year}`).then(r => r.data);

/** Get driver season stats */
export const getDriverStats = (driverId, year = 2025) =>
  api.get(`/drivers/${driverId}/stats?year=${year}`).then(r => r.data);

/** Get telemetry data */
export const getTelemetry = (year, round, session, driver) =>
  api.get(`/telemetry/${year}/${round}/${session}/${driver}`).then(r => r.data);

/** Get race predictions */
export const getPredictions = (year, round) =>
  api.get(`/predictions/${year}/${round}`).then(r => r.data);

/** Health check */
export const healthCheck = () => api.get('/health').then(r => r.data);

export default api;
"""

print('Writing frontend files...')
for path, content in files.items():
    full_path = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f'  Created: {path}')

print('\nFrontend base files complete.')
