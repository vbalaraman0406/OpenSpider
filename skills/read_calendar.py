import json
import os

path = 'workspace/f1_calendar_2026.json'
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
    for race in data[:5]:
        print(json.dumps(race, indent=2))
else:
    print('FILE NOT FOUND')
