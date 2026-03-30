#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

cron_path = os.path.join(os.getcwd(), 'workspace', 'cron_jobs.json')
with open(cron_path, 'r') as f:
    cron_data = json.load(f)

now_utc = datetime.now(timezone.utc)
now_ms = int(now_utc.timestamp() * 1000)

for job in cron_data.get('jobs', []):
    if job.get('filename') == 'Trump Truth Social Monitor':
        old_ts = job.get('lastRunTimestamp')
        job['lastRunTimestamp'] = now_ms
        print(f'Updated lastRunTimestamp from {old_ts} to {now_ms}')
        print(f'Current UTC: {now_utc.isoformat()}')
        break

with open(cron_path, 'w') as f:
    json.dump(cron_data, f, indent=2)
print('cron_jobs.json updated successfully.')
print('STATUS: FETCH_FAILED_INFRA')
