import os
import datetime

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# First, read the frontend api.ts to see what paths it calls
with open(os.path.join(BASE, 'frontend/src/api.ts'), 'r') as f:
    api_ts = f.read()
print('=== Frontend api.ts ===')
print(api_ts)
print()

# Read race.py router
with open(os.path.join(BASE, 'backend/routers/race.py'), 'r') as f:
    race_py = f.read()
print('=== Race router routes ===')
for line in race_py.split('\n'):
    if 'prefix' in line or '@router' in line or 'def ' in line:
        print(line)
print()

# Read drivers.py router  
with open(os.path.join(BASE, 'backend/routers/drivers.py'), 'r') as f:
    drivers_py = f.read()
print('=== Drivers router routes ===')
for line in drivers_py.split('\n'):
    if 'prefix' in line or '@router' in line or 'def ' in line:
        print(line)
