import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

job = jobs[3]
print(f'NAME: {job.get("name","?")}')
print(f'preferredTime: {job.get("preferredTime","N/A")}')
print(f'intervalHours: {job.get("intervalHours","N/A")}')
print(f'whatsappGroup: {job.get("whatsappGroup","N/A")}')
print(f'enabled: {job.get("enabled","N/A")}')
print('PROMPT:')
print(job.get('prompt',''))
