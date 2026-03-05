import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print(f'Total jobs before: {len(jobs)}')

removed = []
kept = []
for job in jobs:
    # Identify malformed baseball jobs: they have 'name' but no 'id', and use 'enabled'/'lastRun'
    job_name = job.get('name', '')
    has_id = 'id' in job
    has_legacy_enabled = 'enabled' in job
    has_legacy_lastRun = 'lastRun' in job
    is_baseball = 'Fantasy Baseball' in job_name
    
    if is_baseball and has_legacy_enabled and not has_id:
        removed.append(job_name)
        print(f'REMOVING malformed job: {job_name}')
    else:
        kept.append(job)
        print(f'KEEPING job: {job.get("id", job.get("name", "unknown"))} - {job_name}')

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(kept, f, indent=2)

print(f'\nRemoved {len(removed)} malformed jobs: {removed}')
print(f'Remaining jobs: {len(kept)}')
