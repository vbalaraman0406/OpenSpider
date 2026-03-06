import json

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

for j in jobs:
    if 'F1 Fantasy' in j.get('name', ''):
        print('=== F1 Fantasy Cron Job ===')
        for k in ['id', 'name', 'status', 'intervalHours', 'preferredTime', 'lastRunTimestamp', 'agentId', 'createdAt', 'enabled']:
            print(f'  {k}: {j.get(k, "MISSING")}')
        print(f'  prompt length: {len(j.get("prompt", ""))} chars')
        print(f'  prompt preview: {j.get("prompt", "")[:200]}...')
        break
else:
    print('ERROR: No F1 Fantasy cron job found in cron_jobs.json')
