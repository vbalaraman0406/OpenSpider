import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print(f'Total jobs before: {len(jobs)}')

removed = []
kept = []
for job in jobs:
    job_name = job.get('name', '')
    if 'Fantasy Baseball' in job_name:
        removed.append(job_name)
        print(f'REMOVING: {job_name} (id: {job.get("id", "none")})')
    else:
        kept.append(job)
        print(f'KEEPING:  {job_name} (id: {job.get("id", "none")})')

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(kept, f, indent=2)

print(f'\nRemoved {len(removed)} baseball jobs: {removed}')
print(f'Remaining jobs: {len(kept)}')
