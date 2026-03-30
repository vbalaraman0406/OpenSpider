#!/usr/bin/env python3
import json
import time
import os

CRON_JOBS_PATH = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'

# Load current cron jobs
with open(CRON_JOBS_PATH, 'r') as f:
    data = json.load(f)

current_ms = int(time.time() * 1000)
updated = False
for job in data:
    if job.get('description') == 'Trump Truth Social Monitor':
        job['lastRunTimestamp'] = current_ms
        updated = True
        break

if updated:
    with open(CRON_JOBS_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'Updated lastRunTimestamp to {current_ms} for Trump Truth Social Monitor.')
else:
    print('Error: Trump Truth Social Monitor job not found.')