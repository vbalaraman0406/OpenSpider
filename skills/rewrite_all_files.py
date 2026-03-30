import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Write backend/main.py
main_py = '''from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import race, drivers
import os

app = FastAPI(title="Pitwall AI", root_path="/f1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(race.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve React frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
'''

path = os.path.join(base, 'backend', 'main.py')
with open(path, 'w') as f:
    f.write(main_py)
print(f'Written: {path}')

# Verify
with open(path) as f:
    content = f.read()
print(f'Verified main.py starts with: {content[:80]}')

# 2. Write app.yaml
app_yaml = '''service: f1
runtime: python311

entrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.main:app --bind :$PORT

instance_class: F2

automatic_scaling:
  min_instances: 0
  max_instances: 3

env_variables:
  PYTHON_ENV: "production"
  PYTHONPATH: /workspace
'''

path = os.path.join(base, 'app.yaml')
with open(path, 'w') as f:
    f.write(app_yaml)
print(f'Written: {path}')

# 3. Write .gcloudignore
gcloudignore = '''frontend/node_modules/
node_modules/
.git/
.gitignore
__pycache__/
*.pyc
.venv/
venv/
frontend/src/
frontend/public/
frontend/vite.config.ts
frontend/tsconfig*.json
frontend/package*.json
frontend/index.html
*.md
.env
*.sh
*.log
'''

path = os.path.join(base, '.gcloudignore')
with open(path, 'w') as f:
    f.write(gcloudignore)
print(f'Written: {path}')

# 4. Write dispatch.yaml
dispatch_yaml = '''dispatch:
  - url: "*/f1/*"
    service: f1
  - url: "*/f1"
    service: f1
'''

path = os.path.join(base, 'dispatch.yaml')
with open(path, 'w') as f:
    f.write(dispatch_yaml)
print(f'Written: {path}')

# 5. Write frontend/vite.config.ts
vite_config = '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/f1/",
  server: {
    proxy: {
      "/f1/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
'''

path = os.path.join(base, 'frontend', 'vite.config.ts')
with open(path, 'w') as f:
    f.write(vite_config)
print(f'Written: {path}')

# 6. Write frontend/src/main.tsx
main_tsx = '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename="/f1">
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
'''

path = os.path.join(base, 'frontend', 'src', 'main.tsx')
with open(path, 'w') as f:
    f.write(main_tsx)
print(f'Written: {path}')

# 7. Write frontend/src/api.ts
api_ts = '''import axios from "axios";

const api = axios.create({ baseURL: "/f1/api" });

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

path = os.path.join(base, 'frontend', 'src', 'api.ts')
with open(path, 'w') as f:
    f.write(api_ts)
print(f'Written: {path}')

print('\n=== ALL FILES WRITTEN SUCCESSFULLY ===')

# Final verification
for rel in ['app.yaml', 'dispatch.yaml', '.gcloudignore', 'backend/main.py', 'frontend/vite.config.ts', 'frontend/src/main.tsx', 'frontend/src/api.ts']:
    full = os.path.join(base, rel)
    with open(full) as f:
        first_line = f.readline().strip()
    print(f'  {rel}: {first_line}')
