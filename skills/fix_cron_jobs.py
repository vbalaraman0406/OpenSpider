import json
import time
import random
import string

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print(f'Found {len(jobs)} jobs')
print('Backing up to cron_jobs.backup.json...')

with open('workspace/cron_jobs.backup.json', 'w') as f:
    json.dump(jobs, f, indent=2)

def gen_id():
    chars = string.ascii_lowercase + string.digits
    return 'cron-' + ''.join(random.choice(chars) for _ in range(9))

for job in jobs:
    name = job.get('name', 'unknown')
    changed = False
    
    # Add missing 'id' field
    if 'id' not in job:
        job['id'] = gen_id()
        changed = True
    
    # Convert 'enabled' to 'status'
    if 'status' not in job:
        if job.get('enabled', True):
            job['status'] = 'enabled'
        else:
            job['status'] = 'disabled'
        changed = True
    
    # Remove old 'enabled' field if present
    if 'enabled' in job:
        del job['enabled']
        changed = True
    
    # Convert 'lastRun' to 'lastRunTimestamp'
    if 'lastRunTimestamp' not in job:
        old_val = job.get('lastRun', None)
        if old_val and isinstance(old_val, (int, float)):
            job['lastRunTimestamp'] = int(old_val)
        else:
            job['lastRunTimestamp'] = None
        changed = True
    
    # Remove old 'lastRun' field if present
    if 'lastRun' in job:
        del job['lastRun']
        changed = True
    
    # Add missing 'agentId'
    if 'agentId' not in job:
        job['agentId'] = 'agent-worker-01'
        changed = True
    
    # Ensure 'createdAt' exists
    if 'createdAt' not in job:
        job['createdAt'] = int(time.time() * 1000)
        changed = True
    
    status_str = '✅ FIXED' if changed else '⏭️ OK'
    print(f'{status_str}: {name}')
    print(f'  id={job["id"]}, status={job["status"]}, lastRunTimestamp={job.get("lastRunTimestamp")}, agentId={job["agentId"]}')

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print(f'\nDone. {len(jobs)} jobs written to cron_jobs.json')
print('Backup saved to cron_jobs.backup.json')
