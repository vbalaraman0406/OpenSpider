import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

required = ['id', 'status', 'lastRunTimestamp', 'agentId', 'name', 'prompt', 'intervalHours']
all_ok = True
for job in jobs:
    name = job.get('name','?')
    missing = [k for k in required if k not in job]
    has_old = [k for k in ['enabled', 'lastRun'] if k in job]
    ok = len(missing) == 0 and len(has_old) == 0
    if not ok:
        all_ok = False
    print(f'{"✅" if ok else "❌"} {name}')
    if missing:
        print(f'  MISSING: {missing}')
    if has_old:
        print(f'  STALE FIELDS: {has_old}')
    print(f'  id={job.get("id")}, status={job.get("status")}, pTime={job.get("preferredTime","N/A")}, interval={job.get("intervalHours")}h')

print(f'\nOverall: {"ALL OK ✅" if all_ok else "ISSUES REMAIN ❌"}')
