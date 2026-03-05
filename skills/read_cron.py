import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print(f'Total jobs: {len(jobs)}')
print('---')
for i, job in enumerate(jobs):
    print(f'\n=== JOB {i+1} ===')
    print(f'  name: {job.get("name", "N/A")}')
    print(f'  id: {job.get("id", "MISSING")}')
    print(f'  status: {job.get("status", "MISSING")}')
    print(f'  enabled: {job.get("enabled", "MISSING")}')
    print(f'  intervalHours: {job.get("intervalHours", "N/A")}')
    print(f'  preferredTime: {job.get("preferredTime", "N/A")}')
    print(f'  lastRun: {job.get("lastRun", "MISSING")}')
    print(f'  lastRunTimestamp: {job.get("lastRunTimestamp", "MISSING")}')
    print(f'  agentId: {job.get("agentId", "MISSING")}')
    print(f'  whatsappGroup: {job.get("whatsappGroup", "MISSING")}')
    print(f'  prompt (first 120 chars): {job.get("prompt", "N/A")[:120]}')
    has_all = all(k in job for k in ['id', 'status', 'lastRunTimestamp', 'agentId'])
    print(f'  SCHEMA OK: {has_all}')
