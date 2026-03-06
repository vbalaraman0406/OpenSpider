import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

for i, job in enumerate(jobs, 1):
    print(f"--- Job {i} ---")
    print(f"Name: {job.get('name')}")
    print(f"ID: {job.get('id')}")
    print(f"Status: {job.get('status')}")
    print(f"Interval (hrs): {job.get('intervalHours')}")
    print(f"Preferred Time: {job.get('preferredTime', 'N/A')}")
    print(f"Last Run: {job.get('lastRunTimestamp')}")
    print(f"Agent: {job.get('agentId', 'N/A')}")
    prompt = job.get('prompt', '')
    print(f"Prompt (first 120 chars): {prompt[:120]}...")
    print()

print(f"Total jobs: {len(jobs)}")
