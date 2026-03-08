import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

for job in jobs:
    if job.get('id') == 'cron-mzyrevand':
        print(json.dumps(job, indent=2))
        break
else:
    print('Job not found')
