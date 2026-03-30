import os

main_py_content = '''from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pitwall.ai API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "..", "frontend", "dist")
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

# Setup FastF1 cache in writable /tmp
CACHE_DIR = "/tmp/fastf1_cache"
try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    pass

# Import routers with try/except
try:
    from backend.routers import race, drivers
    logger.info("Imported routers via backend.routers")
except ImportError:
    try:
        from routers import race, drivers
        logger.info("Imported routers via routers")
    except ImportError:
        race = None
        drivers = None
        logger.warning("Could not import routers")

# ---- API ROUTES FIRST (before catch-all) ----

@app.get("/f1/api/health")
@app.get("/api/health")
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "pitwall-ai", "version": "f1live2"})

@app.get("/f1/api/status")
async def status():
    return JSONResponse({
        "routers_loaded": race is not None,
        "frontend_exists": os.path.isfile(INDEX_HTML),
        "assets_exist": os.path.isdir(ASSETS_DIR),
        "cache_dir": CACHE_DIR
    })

# Mount API routers BEFORE static files and catch-all
if race:
    app.include_router(race.router, prefix="/f1/api", tags=["races"])
    logger.info("Mounted race router at /f1/api")
if drivers:
    app.include_router(drivers.router, prefix="/f1/api", tags=["drivers"])
    logger.info("Mounted drivers router at /f1/api")

# ---- STATIC FILES (after API routes) ----
if os.path.isdir(ASSETS_DIR):
    app.mount("/f1/assets", StaticFiles(directory=ASSETS_DIR), name="static-assets")
    logger.info(f"Mounted static assets from {ASSETS_DIR}")

# ---- SPA CATCH-ALL (LAST) ----
@app.get("/f1")
@app.get("/f1/")
@app.get("/f1/{path:path}")
async def serve_spa(request: Request, path: str = ""):
    # Never serve SPA for API or asset routes
    if path.startswith("api/") or path.startswith("assets/"):
        return JSONResponse({"error": "not found"}, status_code=404)
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    return JSONResponse({"error": "frontend not built"}, status_code=500)
'''

target = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py'
with open(target, 'w') as f:
    f.write(main_py_content)
print(f'Written {len(main_py_content)} bytes to {target}')

# Verify
with open(target, 'r') as f:
    content = f.read()
print('Health route present:', '@app.get("/f1/api/health")' in content)
print('Router mount present:', 'app.include_router' in content)
print('SPA catch-all present:', '/f1/{path:path}' in content)
