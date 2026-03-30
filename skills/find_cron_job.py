import json
import os
import sys

file_path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    job = None
    for item in data:
        if 'description' in item and 'Trump Truth Social Monitor' in item['description']:
            job = item
            break
    if job:
        print(f"Job found: {job['description']}")
        print(f"lastRunTimestamp: {job.get('lastRunTimestamp', 'Not found')}")
        print(f"intervalHours: {job.get('intervalHours', 'Not found')}")
        sys.exit(0)
    else:
        print("Job 'Trump Truth Social Monitor' not found in cron_jobs.json")
        sys.exit(1)
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)