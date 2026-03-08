import os

base = 'workspace/pitwall-ai/frontend'

dirs = [
    f'{base}/src/components',
    f'{base}/src/pages',
    f'{base}/public',
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

files = {}

files[f'{base}/package.json'] = '''{
  "name": "pitwall-ai-frontend",
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
    "axios": "^1.6.2",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
'''

files[f'{base}/vite.config.ts'] = '''import { defineConfig } from "vite";
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
'''

files[f'{base}/tailwind.config.js'] = '''/** @type {import("tailwindcss").Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "f1-red": "#e10600",
        "f1-dark": "#0f0f0f",
        "f1-gray": "#1a1a1a",
        "f1-card": "#1e1e1e",
        "f1-border": "#2a2a2a",
        "f1-muted": "#888888",
        "f1-white": "#ffffff",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
'''

files[f'{base}/postcss.config.js'] = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
'''

files[f'{base}/tsconfig.json'] = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
'''

files[f'{base}/index.html'] = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
    <title>PITWALL.ai — F1 Analytics</title>
  </head>
  <body class="bg-f1-dark text-f1-white">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''

files[f'{base}/src/main.tsx'] = '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
'''

files[f'{base}/src/index.css'] = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-f1-dark text-f1-white antialiased;
  }
  ::-webkit-scrollbar {
    width: 8px;
  }
  ::-webkit-scrollbar-track {
    @apply bg-f1-dark;
  }
  ::-webkit-scrollbar-thumb {
    @apply bg-f1-border rounded-full;
  }
  ::-webkit-scrollbar-thumb:hover {
    @apply bg-f1-muted;
  }
}

.team-mercedes { color: #00D2BE; }
.team-ferrari { color: #DC0000; }
.team-redbull { color: #3671C6; }
.team-mclaren { color: #FF8700; }
.team-alpine { color: #0090FF; }
.team-aston { color: #006F62; }
.team-williams { color: #005AFF; }
.team-haas { color: #FFFFFF; }
.team-sauber { color: #52E252; }
.team-rb { color: #6692FF; }
'''

files[f'{base}/src/App.tsx'] = '''import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import RaceDetail from "./pages/RaceDetail";
import Drivers from "./pages/Drivers";
import Compare from "./pages/Compare";

export default function App() {
  return (
    <div className="min-h-screen bg-f1-dark">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/race/:year/:round" element={<RaceDetail />} />
          <Route path="/drivers/:year" element={<Drivers />} />
          <Route path="/compare" element={<Compare />} />
        </Routes>
      </main>
    </div>
  );
}
'''

files[f'{base}/src/api.ts'] = '''import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const getRaces = (year: number) => api.get(`/races/${year}`);
export const getRaceResults = (year: number, round: number, session?: string) =>
  api.get(`/races/${year}/${round}/results`, { params: { session } });
export const getLaps = (year: number, round: number, driver?: string) =>
  api.get(`/races/${year}/${round}/laps`, { params: { driver } });
export const getTelemetry = (year: number, round: number, driver: string) =>
  api.get(`/races/${year}/${round}/telemetry/${driver}`);
export const getStrategy = (year: number, round: number) =>
  api.get(`/races/${year}/${round}/strategy`);
export const getDrivers = (year: number) => api.get(`/drivers/${year}`);
export const getDriverStats = (year: number, code: string) =>
  api.get(`/drivers/${year}/${code}/stats`);
export const compareDrivers = (year: number, drivers: string[]) =>
  api.get(`/drivers/${year}/compare`, { params: { drivers: drivers.join(",") } });

export default api;
'''

print('Phase 1 files written successfully.')
print(f'Total files: {len(files)}')

for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content)
    print(f'  ✅ {path}')

print('\nPhase 1 complete. Run build_frontend_p2.py for components and pages.')
