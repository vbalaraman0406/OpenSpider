import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print(f'Total jobs in cron_jobs.json: {len(jobs)}')
print()
for i, job in enumerate(jobs, 1):
    name = job.get('name', 'NO NAME')
    jid = job.get('id', 'NO ID')
    status = job.get('status', 'NO STATUS')
    time = job.get('preferredTime', 'NO TIME')
    has_lrt = 'lastRunTimestamp' in job
    has_agent = 'agentId' in job
    has_interval = 'intervalHours' in job
    has_prompt = 'prompt' in job
    is_baseball = 'baseball' in name.lower() or 'baseball' in job.get('prompt','').lower()
    print(f'Job {i}: {name}')
    print(f'  id={jid}, status={status}, time={time}')
    print(f'  lastRunTimestamp={has_lrt}, agentId={has_agent}, intervalHours={has_interval}, prompt={has_prompt}')
    print(f'  Baseball? {is_baseball}')
    # Check for old malformed fields
    old = [k for k in ['enabled','lastRun'] if k in job]
    if old:
        print(f'  ⚠️ OLD FIELDS: {old}')
    print()
