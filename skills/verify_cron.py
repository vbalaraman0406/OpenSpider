import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

required_fields = ['id', 'status', 'lastRunTimestamp', 'agentId', 'intervalHours', 'preferredTime', 'prompt']

print(f'Total jobs: {len(jobs)}\n')
print(f'{"#":<3} {"ID":<20} {"Name":<55} {"Time":<6} {"Status":<10} {"lastRunTS":<15} {"agentId":<18} {"Missing Fields"}')
print('-' * 160)

for i, job in enumerate(jobs, 1):
    jid = job.get('id', 'MISSING')
    name = job.get('name', 'MISSING')[:54]
    time = job.get('preferredTime', 'MISSING')
    status = job.get('status', 'MISSING')
    lrt = job.get('lastRunTimestamp')
    lrt_str = str(lrt) if lrt is not None else 'null'
    agent = job.get('agentId', 'MISSING')
    missing = [f for f in required_fields if f not in job]
    missing_str = ', '.join(missing) if missing else 'NONE'
    print(f'{i:<3} {jid:<20} {name:<55} {time:<6} {status:<10} {lrt_str:<15} {agent:<18} {missing_str}')

# Check for old malformed fields
print('\n--- Malformed Field Check ---')
for i, job in enumerate(jobs, 1):
    old_fields = []
    if 'enabled' in job:
        old_fields.append('enabled')
    if 'lastRun' in job:
        old_fields.append('lastRun')
    if not job.get('id', '').startswith('cron-'):
        old_fields.append('id not cron-prefixed')
    name = job.get('name', 'UNKNOWN')[:50]
    if old_fields:
        print(f'  Job {i} ({name}): ⚠️  Has old fields: {old_fields}')
    else:
        print(f'  Job {i} ({name}): ✅ Clean schema')

# Check baseball jobs specifically
print('\n--- Baseball Job Check ---')
baseball_jobs = [j for j in jobs if 'baseball' in j.get('name','').lower() or 'baseball' in j.get('prompt','').lower()]
if baseball_jobs:
    for bj in baseball_jobs:
        print(f'  ✅ Found: {bj.get("name")} (id={bj.get("id")}, time={bj.get("preferredTime")}, status={bj.get("status")})')
else:
    print('  ❌ NO baseball jobs found in cron_jobs.json!')
