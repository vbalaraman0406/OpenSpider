import json

with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

for job in data:
    if job.get('id') == 'cron-hckpx7ers':
        print('FULL PROMPT:')
        print(job['prompt'])
        print('---')
        print('ALL FIELDS:')
        for k, v in job.items():
            if k != 'prompt':
                print(f'  {k}: {v}')
        break
