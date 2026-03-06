import json

# Read F1 calendar
with open('workspace/f1_calendar_2026.json') as f:
    cal = json.load(f)

# Find Round 1
for race in cal:
    if race.get('round') == 1 or 'Austral' in str(race.get('name','')):
        print('=== AUSTRALIAN GP ENTRY ===')
        print(json.dumps(race, indent=2))
        break

print()

# Read cron jobs
with open('workspace/cron_jobs.json') as f:
    jobs = json.load(f)

for job in jobs:
    if 'F1' in str(job.get('name','')) or job.get('id') == 'cron-hc3fjkb7d':
        print('=== F1 FANTASY CRON JOB ===')
        print(json.dumps(job, indent=2))
        break
