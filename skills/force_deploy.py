import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Add a timestamp comment to main.py to force GCP to detect file changes
main_path = os.path.join(base, 'backend/main.py')
with open(main_path, 'r') as f:
    content = f.read()

# Add deployment timestamp comment at the top
timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
if '# Deploy timestamp:' in content:
    # Replace existing timestamp
    lines = content.split('\n')
    lines = [l for l in lines if not l.startswith('# Deploy timestamp:')]
    content = '\n'.join(lines)

content = f'# Deploy timestamp: {timestamp}\n' + content

with open(main_path, 'w') as f:
    f.write(content)
print(f'Added deploy timestamp to main.py: {timestamp}')

# Also verify the import fixes are in place
race_path = os.path.join(base, 'backend/routers/race.py')
with open(race_path, 'r') as f:
    race_content = f.read()

if 'from backend.data.fastf1_loader' in race_content:
    print('race.py imports: CORRECT (backend.data.fastf1_loader)')
else:
    print('race.py imports: WRONG - still using old imports!')
    # Fix it
    race_content = race_content.replace('from data.fastf1_loader import', 'from backend.data.fastf1_loader import')
    race_content = race_content.replace('from data.models import', 'from backend.data.models import')
    with open(race_path, 'w') as f:
        f.write(race_content)
    print('race.py imports: FIXED')

drivers_path = os.path.join(base, 'backend/routers/drivers.py')
with open(drivers_path, 'r') as f:
    drivers_content = f.read()

if 'from backend.data.fastf1_loader' in drivers_content:
    print('drivers.py imports: CORRECT (backend.data.fastf1_loader)')
else:
    print('drivers.py imports: WRONG - still using old imports!')
    drivers_content = drivers_content.replace('from data.fastf1_loader import', 'from backend.data.fastf1_loader import')
    drivers_content = drivers_content.replace('from data.models import', 'from backend.data.models import')
    with open(drivers_path, 'w') as f:
        f.write(drivers_content)
    print('drivers.py imports: FIXED')

# Verify __init__.py exists in backend/
init_path = os.path.join(base, 'backend/__init__.py')
if not os.path.exists(init_path):
    with open(init_path, 'w') as f:
        f.write('')
    print('Created backend/__init__.py')
else:
    print('backend/__init__.py exists')

print('\nAll files ready for deployment.')
