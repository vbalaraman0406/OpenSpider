import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Created: {path}')

# package.json
write('frontend/package.json', '''{
  "name": "pitwall-ai",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "recharts": "^2.10.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.0"
  }
}
''')

# vite.config.js
write('frontend/vite.config.js', '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
''')

# postcss.config.js
write('frontend/postcss.config.js', '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
''')

# tailwind.config.js
write('frontend/tailwind.config.js', '''/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        pitwall: {
          dark: "#0f0f1a",
          card: "#1a1a2e",
          surface: "#16213e",
          red: "#e10600",
          white: "#ffffff",
          gray: "#8892a4",
          border: "#2a2a4a",
        },
        team: {
          redbull: "#3671C6",
          mclaren: "#FF8000",
          ferrari: "#E8002D",
          mercedes: "#27F4D2",
          astonmartin: "#229971",
          alpine: "#FF87BC",
          williams: "#64C4FF",
          rb: "#6692FF",
          sauber: "#52E252",
          haas: "#B6BABD",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
''')

# index.html
write('frontend/index.html', '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
    <title>Pitwall.ai | F1 Analytics</title>
  </head>
  <body class="bg-pitwall-dark text-white">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
''')

# src/main.jsx
write('frontend/src/main.jsx', '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
''')

# src/index.css
write('frontend/src/index.css', '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-pitwall-dark text-white antialiased;
    font-family: "Inter", system-ui, sans-serif;
  }

  ::-webkit-scrollbar {
    width: 6px;
  }

  ::-webkit-scrollbar-track {
    @apply bg-pitwall-dark;
  }

  ::-webkit-scrollbar-thumb {
    @apply bg-pitwall-border rounded-full;
  }
}

@layer components {
  .card {
    @apply bg-pitwall-card border border-pitwall-border rounded-lg p-6;
  }

  .btn-primary {
    @apply bg-pitwall-red hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg transition-all duration-200;
  }

  .btn-secondary {
    @apply bg-pitwall-surface hover:bg-pitwall-border text-white font-medium py-2 px-4 rounded-lg border border-pitwall-border transition-all duration-200;
  }

  .data-table {
    @apply w-full text-sm;
  }

  .data-table th {
    @apply text-left text-pitwall-gray font-medium uppercase text-xs tracking-wider py-3 px-4 border-b border-pitwall-border;
  }

  .data-table td {
    @apply py-3 px-4 border-b border-pitwall-border/50;
  }

  .data-table tr:hover td {
    @apply bg-pitwall-surface/50;
  }

  .stat-value {
    @apply text-3xl font-bold font-mono;
  }

  .stat-label {
    @apply text-xs text-pitwall-gray uppercase tracking-wider mt-1;
  }

  .compound-soft {
    @apply bg-red-500 text-white;
  }

  .compound-medium {
    @apply bg-yellow-500 text-black;
  }

  .compound-hard {
    @apply bg-white text-black;
  }

  .compound-intermediate {
    @apply bg-green-500 text-white;
  }

  .compound-wet {
    @apply bg-blue-500 text-white;
  }
}
''')

# src/App.jsx
write('frontend/src/App.jsx', '''import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import RaceDashboard from "./pages/RaceDashboard";
import DriverStats from "./pages/DriverStats";

export default function App() {
  return (
    <div className="min-h-screen bg-pitwall-dark">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/race/:year/:round" element={<RaceDashboard />} />
          <Route path="/drivers" element={<DriverStats />} />
        </Routes>
      </main>
    </div>
  );
}
''')

# src/components/Navbar.jsx
write('frontend/src/components/Navbar.jsx', '''import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const RACES_2025 = [
  { round: 1, name: "Australian GP", flag: "\ud83c\udde6\ud83c\uddfa" },
  { round: 2, name: "Chinese GP", flag: "\ud83c\udde8\ud83c\uddf3" },
  { round: 3, name: "Japanese GP", flag: "\ud83c\uddef\ud83c\uddf5" },
  { round: 4, name: "Bahrain GP", flag: "\ud83c\udde7\ud83c\udded" },
  { round: 5, name: "Saudi Arabian GP", flag: "\ud83c\uddf8\ud83c\udde6" },
  { round: 6, name: "Miami GP", flag: "\ud83c\uddfa\ud83c\uddf8" },
  { round: 7, name: "Emilia Romagna GP", flag: "\ud83c\uddee\ud83c\uddf9" },
  { round: 8, name: "Monaco GP", flag: "\ud83c\uddf2\ud83c\udde8" },
  { round: 9, name: "Spanish GP", flag: "\ud83c\uddea\ud83c\uddf8" },
  { round: 10, name: "Canadian GP", flag: "\ud83c\udde8\ud83c\udde6" },
  { round: 11, name: "Austrian GP", flag: "\ud83c\udde6\ud83c\uddf9" },
  { round: 12, name: "British GP", flag: "\ud83c\uddec\ud83c\udde7" },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [raceDropdown, setRaceDropdown] = useState(false);
  const navigate = useNavigate();

  return (
    <nav className="bg-pitwall-card border-b border-pitwall-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-pitwall-red rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">P</span>
            </div>
            <span className="text-xl font-bold">
              Pitwall<span className="text-pitwall-red">.ai</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="text-pitwall-gray hover:text-white transition-colors font-medium">
              Home
            </Link>

            {/* Race Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setRaceDropdown(!raceDropdown)}
                className="text-pitwall-gray hover:text-white transition-colors font-medium flex items-center space-x-1"
              >
                <span>Races</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {raceDropdown && (
                <div className="absolute top-full mt-2 w-64 bg-pitwall-surface border border-pitwall-border rounded-lg shadow-xl py-2 max-h-80 overflow-y-auto">
                  {RACES_2025.map((race) => (
                    <button
                      key={race.round}
                      onClick={() => {
                        navigate(`/race/2025/${race.round}`);
                        setRaceDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-pitwall-card text-sm flex items-center space-x-2"
                    >
                      <span>{race.flag}</span>
                      <span>R{race.round} - {race.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <Link to="/drivers" className="text-pitwall-gray hover:text-white transition-colors font-medium">
              Drivers
            </Link>

            <div className="h-6 w-px bg-pitwall-border" />

            <span className="text-xs text-pitwall-gray font-mono bg-pitwall-surface px-3 py-1 rounded-full">
              2025 SEASON
            </span>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-pitwall-gray hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden border-t border-pitwall-border">
          <div className="px-4 py-3 space-y-2">
            <Link to="/" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Home</Link>
            <Link to="/race/2025/1" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Australian GP</Link>
            <Link to="/drivers" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Drivers</Link>
          </div>
        </div>
      )}
    </nav>
  );
}
''')

print('Batch 3 complete: package.json, vite config, tailwind config, index.html, main.jsx, index.css, App.jsx, Navbar.jsx')
