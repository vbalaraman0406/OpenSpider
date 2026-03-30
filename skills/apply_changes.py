import os

# 1. Update backend/main.py
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
        # Serve static files if they exist, otherwise serve index.html for SPA routing
        file_path = os.path.join(frontend_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
'''

with open('workspace/pitwall-ai/backend/main.py', 'w') as f:
    f.write(main_py)
print('Written: backend/main.py')

# 2. Update frontend/vite.config.ts
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

with open('workspace/pitwall-ai/frontend/vite.config.ts', 'w') as f:
    f.write(vite_config)
print('Written: frontend/vite.config.ts')

# 3. Update frontend/src/main.tsx
# First read current to understand structure
with open('workspace/pitwall-ai/frontend/src/main.tsx') as f:
    current_main_tsx = f.read()
print(f'Current main.tsx:\n{current_main_tsx}')

# Update with basename
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

with open('workspace/pitwall-ai/frontend/src/main.tsx', 'w') as f:
    f.write(main_tsx)
print('Written: frontend/src/main.tsx')

# 4. Update frontend/src/api.ts
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

with open('workspace/pitwall-ai/frontend/src/api.ts', 'w') as f:
    f.write(api_ts)
print('Written: frontend/src/api.ts')

# 5. Update app.yaml - add service: f1
app_yaml = '''service: f1
runtime: python311

entrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.main:app --bind :$PORT

instance_class: F2

automatic_scaling:
  min_instances: 0
  max_instances: 3

env_variables:
  PYTHON_ENV: "production"
'''

with open('workspace/pitwall-ai/app.yaml', 'w') as f:
    f.write(app_yaml)
print('Written: app.yaml')

# 6. Create/update dispatch.yaml
dispatch_yaml = '''dispatch:
  - url: "*/f1/*"
    service: f1
  - url: "*/f1"
    service: f1
'''

with open('workspace/pitwall-ai/dispatch.yaml', 'w') as f:
    f.write(dispatch_yaml)
print('Written: dispatch.yaml')

print('\nAll files updated successfully!')
