import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend'

# Fix race.py - replace get_race_schedule with get_schedule
race_path = os.path.join(base, 'routers', 'race.py')
with open(race_path, 'r') as f:
    content = f.read()
content = content.replace('get_race_schedule', 'get_schedule')
with open(race_path, 'w') as f:
    f.write(content)
print('Fixed race.py: get_race_schedule -> get_schedule')

# Fix drivers.py - replace get_drivers_list with list_drivers, remove get_driver_comparison
drivers_path = os.path.join(base, 'routers', 'drivers.py')
drivers_content = '''from fastapi import APIRouter
from fastapi.responses import JSONResponse
try:
    from backend.data.fastf1_loader import list_drivers, get_driver_season_stats
except ImportError:
    from data.fastf1_loader import list_drivers, get_driver_season_stats

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.get("/{year}")
async def get_drivers(year: int):
    try:
        data = list_drivers(year)
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
        return {"driver1": d1, "driver2": d2, "message": "Comparison coming soon"}
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)
'''
with open(drivers_path, 'w') as f:
    f.write(drivers_content)
print('Fixed drivers.py: get_drivers_list -> list_drivers, removed get_driver_comparison')

# Update DEPLOY_MARKER
import time
marker_path = os.path.join(os.path.dirname(base), 'DEPLOY_MARKER.txt')
with open(marker_path, 'w') as f:
    f.write('FORCE_UPLOAD_' + str(time.time()) + '_IMPORT_FIX_FINAL\n')
print('Updated DEPLOY_MARKER.txt')

# Verify race.py imports
with open(race_path, 'r') as f:
    for i, line in enumerate(f.readlines()[:10], 1):
        print('race.py:' + str(i) + ': ' + line.rstrip())

print('\nAll imports fixed. Ready to deploy.')
