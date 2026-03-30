import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Write simplified App.tsx
app_tsx = 'export default function App() {\n  return (\n    <div style={{backgroundColor:"#0a0a0f",color:"white",minHeight:"100vh",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",fontFamily:"sans-serif"}}>\n      <h1 style={{fontSize:"3rem",marginBottom:"1rem"}}>Pitwall.ai</h1>\n      <p style={{color:"#e10600",fontSize:"1.5rem"}}>F1 Analytics Dashboard</p>\n      <p style={{color:"#888",marginTop:"2rem"}}>Dashboard is loading... If you see this, React is working!</p>\n    </div>\n  );\n}\n'
with open(os.path.join(BASE, 'frontend/src/App.tsx'), 'w') as f:
    f.write(app_tsx)
print('Wrote App.tsx')

# 2. Write simplified main.tsx
main_tsx = 'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\n\nReactDOM.createRoot(document.getElementById("root")!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n'
with open(os.path.join(BASE, 'frontend/src/main.tsx'), 'w') as f:
    f.write(main_tsx)
print('Wrote main.tsx')

# 3. Delete vite.config.ts if exists
vite_ts = os.path.join(BASE, 'frontend/vite.config.ts')
if os.path.exists(vite_ts):
    os.remove(vite_ts)
    print('Deleted vite.config.ts')

# 4. Write clean vite.config.js
vite_config = 'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n\nexport default defineConfig({\n  plugins: [react()],\n  base: "/f1/",\n  build: {\n    outDir: "dist",\n    rollupOptions: {\n      output: {\n        manualChunks: undefined,\n      },\n    },\n  },\n});\n'
with open(os.path.join(BASE, 'frontend/vite.config.js'), 'w') as f:
    f.write(vite_config)
print('Wrote vite.config.js')

# 5. Write correct index.html
index_html = '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n    <title>Pitwall.ai - F1 Analytics</title>\n  </head>\n  <body>\n    <div id="root"></div>\n    <script type="module" src="/src/main.tsx"></script>\n  </body>\n</html>\n'
with open(os.path.join(BASE, 'frontend/index.html'), 'w') as f:
    f.write(index_html)
print('Wrote index.html')

# 6. Write fixed backend/main.py
main_py = '''from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI(title="Pitwall.ai API")

# Determine base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "..", "frontend", "dist")
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

# Setup FastF1 cache
CACHE_DIR = "/tmp/fastf1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Import routers with try/except
try:
    from backend.routers import race, drivers
except ImportError:
    try:
        from routers import race, drivers
    except ImportError:
        race = None
        drivers = None

# Mount API routers
if race:
    app.include_router(race.router, prefix="/f1/api")
if drivers:
    app.include_router(drivers.router, prefix="/f1/api")


@app.get("/f1/api/health")
async def health():
    return JSONResponse({"status": "ok", "service": "pitwall-ai"})


# Mount static assets
if os.path.isdir(ASSETS_DIR):
    app.mount("/f1/assets", StaticFiles(directory=ASSETS_DIR), name="static-assets")


@app.get("/f1")
@app.get("/f1/")
@app.get("/f1/{path:path}")
async def serve_spa(request: Request, path: str = ""):
    if path.startswith("api/") or path.startswith("assets/"):
        return JSONResponse({"error": "not found"}, status_code=404)
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    return JSONResponse({"error": "frontend not built"}, status_code=500)
'''
with open(os.path.join(BASE, 'backend/main.py'), 'w') as f:
    f.write(main_py)
print('Wrote backend/main.py')

print('\nAll files written successfully!')
