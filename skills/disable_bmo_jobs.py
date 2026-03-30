import json

path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'

with open(path, 'r') as f:
    data = json.load(f)

target_ids = ['cron-toch3vvpr', 'cron-cj5nm7e4d']
disabled = []

for j in data:
    if j.get('id') in target_ids:
        j['status'] = 'disabled'
        disabled.append({'id': j['id'], 'description': j['description'], 'status': j['status']})

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print(f'Disabled {len(disabled)} jobs:')
for d in disabled:
    print(json.dumps(d))
