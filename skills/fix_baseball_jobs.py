import json
import time
import random
import string

def gen_id():
    chars = string.ascii_lowercase + string.digits
    return 'cron-' + ''.join(random.choice(chars) for _ in range(9))

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

# Remove any existing baseball jobs (safety)
jobs = [j for j in jobs if 'baseball' not in j.get('name','').lower() and 'baseball' not in j.get('prompt','').lower()]

now_ts = int(time.time() * 1000)

baseball_job_1 = {
    "id": gen_id(),
    "name": "Fantasy Baseball Heartbeat — Automated Lineup Optimizer",
    "prompt": "Check Yahoo Fantasy Baseball lineup for today. Optimize the starting lineup based on pitcher matchups, player status (injured/benched/day-off), and recent performance. Send lineup optimization recommendations email to BOTH coolvishnu@gmail.com AND jacob.sorensen@gmail.com separately using send_email. Email subject: ⚾ Fantasy Baseball Lineup Optimizer — [today's date]. Only run on days when MLB games are scheduled.",
    "intervalHours": 24,
    "preferredTime": "08:00",
    "status": "enabled",
    "lastRunTimestamp": 0,
    "agentId": "agent-worker-01",
    "createdAt": now_ts
}

baseball_job_2 = {
    "id": gen_id(),
    "name": "Fantasy Baseball Morning Brief — Daily 9 AM Email",
    "prompt": "Fetch the latest Yahoo Fantasy Baseball updates including roster news, injury reports, waiver wire recommendations, and matchup previews. Send a Fantasy Baseball Morning Brief email to BOTH coolvishnu@gmail.com AND jacob.sorensen@gmail.com separately using send_email. Email subject: ⚾ Fantasy Baseball Morning Brief — [today's date]. Only run on market working days (Mon-Fri, skip weekends and US holidays).",
    "intervalHours": 24,
    "preferredTime": "09:00",
    "status": "enabled",
    "lastRunTimestamp": 0,
    "agentId": "agent-worker-01",
    "createdAt": now_ts
}

jobs.append(baseball_job_1)
jobs.append(baseball_job_2)

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print(f'Done. Total jobs now: {len(jobs)}')
for j in jobs:
    print(f'  {j["id"]} | {j["name"]} | {j["preferredTime"]} | {j["status"]}')
