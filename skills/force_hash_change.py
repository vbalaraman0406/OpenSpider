import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
timestamp = str(time.time())

# Force hash change in fastf1_loader.py
loader_path = os.path.join(base, 'backend/data/fastf1_loader.py')
with open(loader_path, 'r') as f:
    content = f.read()
# Remove old force comments
lines = [l for l in content.split('\n') if not l.startswith('# FORCE_DEPLOY_')]
content = '\n'.join(lines)
content = f'# FORCE_DEPLOY_{timestamp}\n' + content
with open(loader_path, 'w') as f:
    f.write(content)
print(f'fastf1_loader.py hash forced: {timestamp}')

# Force hash change in main.py
main_path = os.path.join(base, 'backend/main.py')
with open(main_path, 'r') as f:
    content = f.read()
lines = [l for l in content.split('\n') if not l.startswith('# FORCE_DEPLOY_') and not l.startswith('# Deploy timestamp:')]
content = '\n'.join(lines)
content = f'# FORCE_DEPLOY_{timestamp}\n' + content
with open(main_path, 'w') as f:
    f.write(content)
print(f'main.py hash forced: {timestamp}')

# Force hash change in race.py
race_path = os.path.join(base, 'backend/routers/race.py')
with open(race_path, 'r') as f:
    content = f.read()
lines = [l for l in content.split('\n') if not l.startswith('# FORCE_DEPLOY_')]
content = '\n'.join(lines)
content = f'# FORCE_DEPLOY_{timestamp}\n' + content
with open(race_path, 'w') as f:
    f.write(content)
print(f'race.py hash forced: {timestamp}')

# Force hash change in drivers.py
drivers_path = os.path.join(base, 'backend/routers/drivers.py')
with open(drivers_path, 'r') as f:
    content = f.read()
lines = [l for l in content.split('\n') if not l.startswith('# FORCE_DEPLOY_')]
content = '\n'.join(lines)
content = f'# FORCE_DEPLOY_{timestamp}\n' + content
with open(drivers_path, 'w') as f:
    f.write(content)
print(f'drivers.py hash forced: {timestamp}')

# Verify key fixes are in place
with open(loader_path, 'r') as f:
    lc = f.read()
if '/tmp/fastf1_cache' in lc:
    print('\nfastf1_loader.py: /tmp/fastf1_cache CORRECT')
else:
    print('\nWARNING: fastf1_loader.py missing /tmp/fastf1_cache!')

with open(race_path, 'r') as f:
    rc = f.read()
if 'from backend.data.fastf1_loader' in rc:
    print('race.py: backend.data.fastf1_loader CORRECT')
else:
    print('WARNING: race.py has wrong imports!')

print('\nAll files ready for forced re-upload.')
