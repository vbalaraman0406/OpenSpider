import json
import os

base = '/Users/vbalaraman/OpenSpider/workspace'

# Read F1 calendar
cal_path = os.path.join(base, 'f1_calendar_2026.json')
if os.path.exists(cal_path):
    with open(cal_path) as f:
        cal = json.load(f)
    for race in cal:
        if race.get('round') == 1 or 'Austral' in str(race.get('name','')):
            print('=== AUSTRALIAN GP ENTRY ===')
            print(json.dumps(race, indent=2))
            break
    else:
        print('No Australian GP found in calendar')
else:
    print('f1_calendar_2026.json NOT FOUND at', cal_path)

print()

# Read cron jobs
cron_path = os.path.join(base, 'cron_jobs.json')
if os.path.exists(cron_path):
    with open(cron_path) as f:
        jobs = json.load(f)
    for job in jobs:
        if 'F1' in str(job.get('name','')) or job.get('id') == 'cron-hc3fjkb7d':
            print('=== F1 FANTASY CRON JOB ===')
            print(json.dumps(job, indent=2))
            break
    else:
        print('No F1 Fantasy cron job found')
else:
    print('cron_jobs.json NOT FOUND at', cron_path)
