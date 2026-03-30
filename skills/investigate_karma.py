import json, os
from datetime import datetime

# 1. Read cron_jobs.json
with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

# Find karma-related jobs
karma_jobs = []
for j in data:
    if 'karma' in json.dumps(j).lower():
        karma_jobs.append(j)

print('=== KARMA CRON JOBS FOUND ===')
for j in karma_jobs:
    print(json.dumps(j, indent=2))

print(f'\n=== CURRENT SYSTEM TIME ===')
now = datetime.now()
print(f'Now: {now.isoformat()}')

# 2. Check memory logs
for date_str in ['2026-03-27', '2026-03-28', '2026-03-26']:
    path = f'workspace/memory/{date_str}.md'
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Search for karma mentions
        lines = content.split('\n')
        karma_lines = [l for l in lines if 'karma' in l.lower() or 'cron' in l.lower()]
        if karma_lines:
            print(f'\n=== KARMA/CRON mentions in {date_str}.md ===')
            for l in karma_lines:
                print(l)
        else:
            print(f'\n=== No karma/cron mentions in {date_str}.md ===')
    else:
        print(f'\n=== File {path} does not exist ===')
