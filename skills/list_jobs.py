import json

with open('./cron_jobs.json', 'r') as f:
    data = json.load(f)

for i, job in enumerate(data):
    name = job.get('name', 'NO NAME')
    print(str(i) + ': ' + name)
