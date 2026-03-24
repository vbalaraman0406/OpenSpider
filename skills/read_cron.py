import json
import os

path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
if os.path.exists(path):
    with open(path, 'r') as f:
        data = json.load(f)
    job = next((j for j in data['jobs'] if j['filename'] == 'Trump Truth Social Monitor'), None)
    if job:
        print(job['lastRunTimestamp'])
    else:
        print('Job not found')
else:
    print('File not found')