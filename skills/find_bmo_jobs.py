import json

with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

for j in data:
    name = j.get('name', '').lower()
    prompt = j.get('prompt', '').lower()
    if 'bmo' in name or 'bmo' in prompt or 'downdetector' in name or 'downdetector' in prompt:
        print(json.dumps(j, indent=2))
        print('---')
