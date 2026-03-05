import json
from datetime import datetime, timezone
import os

# Read cron jobs
with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

print('=== ALL CRON JOBS ===')
for j in data:
    jid = j.get('id', '?')
    desc = j.get('description', j.get('name', '?'))[:100]
    status = j.get('status', '?')
    print(f'{jid} | {desc} | {status}')

print('\n=== BASEBALL/MLB SEARCH ===')
keywords = ['baseball', 'mlb', 'spring training', 'batting', 'pitcher', 'home run']
found = []
for j in data:
    searchable = json.dumps(j).lower()
    if any(k in searchable for k in keywords):
        found.append(j)

if not found:
    print('NO BASEBALL/MLB CRON JOBS FOUND')
else:
    for j in found:
        print(json.dumps(j, indent=2))
        ts = j.get('lastRunTimestamp')
        if ts:
            from zoneinfo import ZoneInfo
            dt = datetime.fromtimestamp(ts/1000 if ts > 1e12 else ts, tz=ZoneInfo('America/Los_Angeles'))
            print(f'Last run (Pacific): {dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")}')
        else:
            print('Last run: NEVER')
        print(f'Status: {j.get("status", "unknown")}')
        pt = j.get('preferredTime', '')
        interval = j.get('intervalHours', '')
        print(f'preferredTime: {pt}, intervalHours: {interval}')
        print('---')

# Check today's memory log
print('\n=== MEMORY LOG 2026-03-05 ===')
log_path = 'workspace/memory/2026-03-05.md'
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        content = f.read()
    lines = content.split('\n')
    baseball_lines = [l for l in lines if any(k in l.lower() for k in keywords)]
    if baseball_lines:
        for l in baseball_lines:
            print(l)
    else:
        print('No baseball-related entries found in today\'s log')
        # Print all lines for context
        print('\nFull log entries (first 2000 chars):')
        print(content[:2000])
else:
    print(f'{log_path} does not exist')
