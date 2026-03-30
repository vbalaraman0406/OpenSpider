import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix race.py imports
race_path = os.path.join(base, 'backend/routers/race.py')
with open(race_path, 'r') as f:
    content = f.read()
content = content.replace('from data.fastf1_loader import', 'from backend.data.fastf1_loader import')
content = content.replace('from data.models import', 'from backend.data.models import')
with open(race_path, 'w') as f:
    f.write(content)
print(f'Fixed race.py imports')

# Fix drivers.py imports
drivers_path = os.path.join(base, 'backend/routers/drivers.py')
with open(drivers_path, 'r') as f:
    content = f.read()
content = content.replace('from data.fastf1_loader import', 'from backend.data.fastf1_loader import')
content = content.replace('from data.models import', 'from backend.data.models import')
with open(drivers_path, 'w') as f:
    f.write(content)
print(f'Fixed drivers.py imports')

# Verify __init__.py files exist
init_files = [
    'backend/__init__.py',
    'backend/routers/__init__.py',
    'backend/data/__init__.py',
]
for init in init_files:
    path = os.path.join(base, init)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('')
        print(f'Created {init}')
    else:
        print(f'Exists: {init}')

# Verify main.py sys.path setup
main_path = os.path.join(base, 'backend/main.py')
with open(main_path, 'r') as f:
    main_content = f.read()

# Check if sys.path includes project root
if 'sys.path' in main_content:
    print('main.py has sys.path setup')
else:
    print('WARNING: main.py missing sys.path setup')

# Print the fixed imports for verification
print('\n--- race.py first 5 lines ---')
with open(race_path, 'r') as f:
    for i, line in enumerate(f):
        if i < 5: print(line.rstrip())

print('\n--- drivers.py first 5 lines ---')
with open(drivers_path, 'r') as f:
    for i, line in enumerate(f):
        if i < 5: print(line.rstrip())

print('\nDone!')
