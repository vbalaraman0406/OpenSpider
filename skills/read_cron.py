import json, os

with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

print(f'Total jobs: {len(data)}')
print(f'Type: {type(data)}')

if isinstance(data, list):
    for i, j in enumerate(data):
        print(f'\n--- Job {i} ---')
        print(json.dumps(j, indent=2)[:500])
elif isinstance(data, dict):
    for k, v in data.items():
        print(f'\n--- Key: {k} ---')
        print(json.dumps(v, indent=2)[:500])
