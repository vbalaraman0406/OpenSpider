import json
import os

path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
print(f'File exists: {os.path.exists(path)}')
print(f'File size: {os.path.getsize(path) if os.path.exists(path) else 0}')

with open(path, 'r') as f:
    data = json.load(f)

print(f'Total jobs: {len(data)}')
print('---ALL JOB NAMES---')
for i, j in enumerate(data):
    name = j.get('name', 'NO NAME')
    status = j.get('status', 'unknown')
    jid = j.get('id', 'no-id')
    if 'BMO' in name.upper() or 'DOWNDETECTOR' in name.upper():
        print(f'  *** MATCH [{i}]: id={jid} | name={name} | status={status}')
    else:
        print(f'  [{i}]: {name}')
