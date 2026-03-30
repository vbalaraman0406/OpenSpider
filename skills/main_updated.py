"""Pitwall.ai - F1 Analytics API"""
import os, sys, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import fastf1

# Ensure backend directory is in sys.path for relative imports
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from routers.race import router as race_router
from routers.drivers import router as drivers_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(BACKEND_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

app = FastAPI(title="Pitwall.ai", description="F1 Analytics API", version="0.1.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(race_router)
app.include_router(drivers_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Mount frontend build at root (AFTER all API routes)
frontend_path = os.path.join(BACKEND_DIR, "..", "frontend", "dist")
frontend_path = os.path.abspath(frontend_path)
if os.path.exists(frontend_path):
    logger.info(f"Mounting frontend static files from: {frontend_path}")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    logger.warning(f"Frontend build not found at: {frontend_path}")
    @app.get("/")
    async def root():
        return {"service": "Pitwall.ai", "version": "0.1.0", "status": "running", "docs": "/docs"}
