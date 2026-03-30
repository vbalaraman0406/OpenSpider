import os
import datetime

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix race.py - remove /api prefix, add /races/{year} route alias
race_py = '''from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/race", tags=["race"])

try:
    from backend.data.fastf1_loader import get_race_schedule, get_race_results as load_race_results, get_race_laps as load_race_laps
except Exception as e:
    print(f"Warning: Could not import fastf1_loader: {e}")
    def get_race_schedule(year): return []
    def load_race_results(year, rnd): return []
    def load_race_laps(year, rnd): return []

@router.get("/schedule/{year}")
async def race_schedule(year: int):
    try:
        data = get_race_schedule(year)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

@router.get("/{year}/{round_num}/results")
async def race_results(year: int, round_num: int):
    try:
        data = load_race_results(year, round_num)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

@router.get("/{year}/{round_num}/laps")
async def race_laps(year: int, round_num: int):
    try:
        data = load_race_laps(year, round_num)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)
'''

# Fix drivers.py - remove /api prefix
drivers_py = '''from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/drivers", tags=["drivers"])

try:
    from backend.data.fastf1_loader import get_drivers_list, get_driver_season_stats, get_driver_comparison
except Exception as e:
    print(f"Warning: Could not import fastf1_loader: {e}")
    def get_drivers_list(year): return []
    def get_driver_season_stats(year, driver): return {}
    def get_driver_comparison(year, d1, d2): return {}

@router.get("/{year}")
async def get_drivers(year: int):
    try:
        data = get_drivers_list(year)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

@router.get("/{year}/{driver}/stats")
async def get_driver_stats(year: int, driver: str):
    try:
        data = get_driver_season_stats(year, driver)
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)

@router.get("/{year}/compare")
async def compare_drivers(year: int, d1: str = "VER", d2: str = "HAM"):
    try:
        data = get_driver_comparison(year, d1, d2)
        return data
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)
'''

# Now fix main.py - add /races/{year} route that aliases /race/schedule/{year}
# and mount routers correctly
timestamp = str(datetime.datetime.now())
main_py = f'''# DEPLOY_MARKER: {timestamp}
import os
import sys

# Ensure project root is on sys.path for GCP App Engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routers import race, drivers

app = FastAPI(
    title="Pitwall.ai - F1 Analytics",
    description="F1 race analytics powered by FastF1",
    version="1.0.0",
    root_path="/f1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable fastf1 cache in writable /tmp directory
try:
    import fastf1
    cache_dir = "/tmp/fastf1_cache"
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)
except Exception:
    pass

# --- API ROUTES (BEFORE static files) ---

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return JSONResponse(content={{"status": "ok", "service": "pitwall-ai-f1"}})

# Mount routers at /api prefix. Routers have /race and /drivers prefixes.
# So final paths: /api/race/..., /api/drivers/...
app.include_router(race.router, prefix="/api", tags=["races"])
app.include_router(drivers.router, prefix="/api", tags=["drivers"])

# Frontend calls /api/races/{{year}} but router defines /api/race/schedule/{{year}}
# Add alias route
@app.get("/api/races/{{year}}")
async def races_alias(year: int):
    try:
        from backend.data.fastf1_loader import get_race_schedule
        data = get_race_schedule(year)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        return JSONResponse(content={{"detail": str(e)}}, status_code=500)

# --- STATIC FILES (SPA catch-all, LAST) ---

frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
frontend_dist = os.path.abspath(frontend_dist)

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/vite.svg")
    async def vite_svg():
        svg_path = os.path.join(frontend_dist, "vite.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path, media_type="image/svg+xml")
        return JSONResponse(content={{"error": "not found"}}, status_code=404)

    @app.get("/{{path:path}}")
    async def serve_spa(path: str):
        file_path = os.path.join(frontend_dist, path)
        if path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        return JSONResponse(content={{"error": "Frontend not built"}}, status_code=500)
else:
    @app.get("/")
    async def no_frontend():
        return JSONResponse(content={{"message": "Pitwall.ai API running. Frontend not found.", "docs": "/f1/docs"}})
'''

# Write all files
with open(os.path.join(BASE, 'backend/routers/race.py'), 'w') as f:
    f.write(race_py)
print('race.py written')

with open(os.path.join(BASE, 'backend/routers/drivers.py'), 'w') as f:
    f.write(drivers_py)
print('drivers.py written')

with open(os.path.join(BASE, 'backend/main.py'), 'w') as f:
    f.write(main_py)
print('main.py written')

# Verify
for fname in ['backend/main.py', 'backend/routers/race.py', 'backend/routers/drivers.py']:
    with open(os.path.join(BASE, fname), 'r') as f:
        content = f.read()
    print(f'{fname}: {len(content)} chars, root_path check: {"root_path" in content if fname == "backend/main.py" else "N/A"}')

print('\nAll router files fixed. Ready for rebuild and deploy.')
