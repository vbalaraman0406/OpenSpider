import json

path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
with open(path, 'r') as f:
    jobs = json.load(f)

# Show all jobs with their key fields
for j in jobs:
    jid = j.get('id', 'NO_ID')
    name = j.get('name', j.get('jobName', 'NO_NAME'))
    status = j.get('status', j.get('enabled', 'NO_STATUS'))
    ptime = j.get('preferredTime', 'NONE')
    prompt_preview = j.get('prompt', '')[:80]
    print(f'{jid} | name={name} | status={status} | time={ptime} | prompt={prompt_preview}...')

# Check for duplicate F1 jobs (cron-tov8tt5py from schedule_task)
dupes = [j for j in jobs if j.get('id') == 'cron-tov8tt5py']
if dupes:
    d = dupes[0]
    print(f'\n--- Duplicate check: cron-tov8tt5py ---')
    print(f'Keys: {list(d.keys())}')
    prompt = d.get('prompt', d.get('task', d.get('content', '')))
    print(f'Has F1 content: {"F1" in str(prompt) or "Fantasy" in str(prompt)}')
    if 'F1' in str(prompt) or 'Fantasy' in str(prompt):
        # Remove duplicate - keep our properly formatted one
        jobs = [j for j in jobs if j.get('id') != 'cron-tov8tt5py']
        with open(path, 'w') as f:
            json.dump(jobs, f, indent=2)
        print('REMOVED duplicate cron-tov8tt5py')
        print(f'Total jobs now: {len(jobs)}')
    else:
        print('cron-tov8tt5py is NOT an F1 job, keeping it.')

# Verify our job
print('\n--- F1 Fantasy Job Verification ---')
our_job = [j for j in jobs if j.get('id') == 'cron-hc3fjkb7d']
if our_job:
    j = our_job[0]
    required = ['id', 'name', 'status', 'intervalHours', 'preferredTime', 'lastRunTimestamp', 'agentId', 'createdAt', 'prompt']
    for k in required:
        val = j.get(k, 'MISSING')
        if k == 'prompt':
            val = f'{len(str(val))} chars'
        print(f'  {k}: {val}')
    print('ALL FIELDS PRESENT:', all(k in j for k in required))
else:
    print('ERROR: cron-hc3fjkb7d not found!')
