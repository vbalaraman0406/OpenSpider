import json, os
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace', 'cron_jobs.json')
with open(path) as f:
    data = json.load(f)
for job in data:
    if job.get('id') == 'cron-fmh7cxq0a':
        print(json.dumps(job, indent=2))
        break
else:
    print('NOT FOUND')
