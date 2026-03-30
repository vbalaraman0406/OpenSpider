import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
main_py_path = f'{base}/backend/main.py'

# Write completely new main.py with correct /f1 prefix handling
# root_path does NOT strip prefix from requests - must handle /f1 explicitly
new_main = '''# DEPLOY_MARKER: FINAL_FIX_v1
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path for GCP App Engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routers import race, drivers

app = FastAPI(
    title="Pitwall.ai - F1 Analytics",
    description="F1 race analytics powered by FastF1",
    version="1.0.0",
    docs_url="/f1/docs",
    openapi_url="/f1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes - mounted at /f1/api prefix
app.include_router(race.router, prefix="/f1/api")
app.include_router(drivers.router, prefix="/f1/api")

# Also mount at /api for backward compatibility
app.include_router(race.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")

# Health endpoints
@app.get("/f1/api/health")
@app.get("/api/health")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "pitwall-ai", "version": "FINAL_FIX_v1"}

# Frontend static files
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
assets_dir = frontend_dist / "assets"
index_html = frontend_dist / "index.html"

if assets_dir.exists():
    # Mount static assets at /f1/assets
    app.mount("/f1/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

# Serve vite.svg
@app.get("/f1/vite.svg")
async def vite_svg():
    svg_path = frontend_dist / "vite.svg"
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    return JSONResponse(content={"error": "not found"}, status_code=404)

# SPA catch-all - serve index.html for all /f1/* routes that aren't API or assets
@app.get("/f1/{path:path}")
async def spa_catchall(path: str):
    if index_html.exists():
        return FileResponse(str(index_html), media_type="text/html")
    return JSONResponse(content={"error": "Frontend not built"}, status_code=500)

@app.get("/f1")
async def spa_root_no_slash():
    if index_html.exists():
        return FileResponse(str(index_html), media_type="text/html")
    return JSONResponse(content={"error": "Frontend not built"}, status_code=500)

# Root redirect
@app.get("/")
async def root():
    return JSONResponse(content={"message": "Pitwall.ai API", "dashboard": "/f1/", "docs": "/f1/docs"})
'''

with open(main_py_path, 'w') as f:
    f.write(new_main)

print('main.py rewritten with explicit /f1 prefix handling')
print('Key changes:')
print('  - Removed root_path (does NOT strip prefix from requests)')
print('  - API routes mounted at /f1/api and /api')
print('  - StaticFiles mounted at /f1/assets (not /assets)')
print('  - SPA catch-all at /f1/{path:path} (not /{path:path})')
print('  - Health endpoints at /f1/api/health, /api/health, /health')
print('  - docs_url set to /f1/docs')

# Also fix api.ts to use /f1/api since we're now mounting at /f1/api
api_ts_path = f'{base}/frontend/src/api.ts'
with open(api_ts_path, 'r') as f:
    api_content = f.read()

print(f'\napi.ts current baseURL:')
if "'/api'" in api_content:
    print('  /api -> changing to /f1/api')
    api_content = api_content.replace("baseURL: '/api'", "baseURL: '/f1/api'")
    with open(api_ts_path, 'w') as f:
        f.write(api_content)
    print('  FIXED: baseURL now /f1/api')
elif "'/f1/api'" in api_content:
    print('  Already /f1/api - OK')
else:
    print(f'  Unknown: {api_content[:200]}')

print('\nAll fixes applied. Ready for rebuild and deploy.')
