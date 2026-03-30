import json
import os
import sys

# Path to cron jobs file
path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'

# Read the file
with open(path, 'r') as f:
    data = json.load(f)

print(f'Total jobs: {len(data)}')
print('\nList of jobs:')
for i, job in enumerate(data):
    print(f'{i+1}. ID: {job.get("id", "N/A")}, Description: {job.get("description", "N/A")}, Interval: {job.get("intervalHours", "N/A")}h, Last Run: {job.get("lastRunTimestamp", "N/A")}')

# Heuristic: delete the job with the oldest last run timestamp (or if none, delete by index)
if data:
    # Find job with oldest last run (or default to first if missing)
    oldest_job = None
    oldest_timestamp = None
    for job in data:
        timestamp = job.get('lastRunTimestamp')
        if timestamp:
            if oldest_timestamp is None or timestamp < oldest_timestamp:
                oldest_timestamp = timestamp
                oldest_job = job
    if oldest_job is None:
        oldest_job = data[0]  # Fallback to first job
    
    print(f'\nDeleting job: ID {oldest_job.get("id")}, Description: {oldest_job.get("description")}')
    data.remove(oldest_job)
    
    # Write back to file
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print('Job deleted successfully. Remaining jobs:', len(data))
else:
    print('No jobs to delete.')
