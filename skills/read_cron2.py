import json
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cron_jobs.json')
print('Looking at:', path)
print('Exists:', os.path.exists(path))

if os.path.exists(path):
    with open(path, 'r') as f:
        data = json.load(f)
    for job in data:
        if job.get('name') == 'Daily Karma Story - WhatsApp':
            print(json.dumps(job, indent=2))
            break
    else:
        print('Job not found. Available jobs:')
        for job in data:
            print(' -', job.get('name'))
else:
    # Try alternate paths
    for p in ['/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', '/Users/vbalaraman/OpenSpider/cron_jobs.json']:
        if os.path.exists(p):
            print('Found at:', p)
            with open(p, 'r') as f:
                data = json.load(f)
            for job in data:
                if job.get('name') == 'Daily Karma Story - WhatsApp':
                    print(json.dumps(job, indent=2))
                    break
            else:
                print('Job not found at', p)
            break
    else:
        print('cron_jobs.json not found anywhere')
