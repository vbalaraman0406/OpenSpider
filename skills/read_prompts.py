import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

for i, job in enumerate(jobs):
    print(f'=== JOB {i+1}: {job.get("name","?")} ===')
    print(f'preferredTime: {job.get("preferredTime","N/A")}')
    print(f'intervalHours: {job.get("intervalHours","N/A")}')
    print(f'whatsappGroup: {job.get("whatsappGroup","N/A")}')
    print(f'PROMPT:')
    print(job.get('prompt',''))
    print('---END---')
    print()
