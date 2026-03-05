import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

job = jobs[0]
print(f'NAME: {job.get("name","?")}')
print(f'preferredTime: {job.get("preferredTime","N/A")}')
print(f'intervalHours: {job.get("intervalHours","N/A")}')
print(f'whatsappGroup: {job.get("whatsappGroup","N/A")}')
print(f'enabled: {job.get("enabled","N/A")}')
print(f'id: {job.get("id","MISSING")}')
print(f'status: {job.get("status","MISSING")}')
print(f'lastRunTimestamp: {job.get("lastRunTimestamp","MISSING")}')
print(f'agentId: {job.get("agentId","MISSING")}')
print('PROMPT:')
print(job.get('prompt',''))

print('\n\n=== JOB 5 ===')
job5 = jobs[4]
print(f'NAME: {job5.get("name","?")}')
print(f'preferredTime: {job5.get("preferredTime","N/A")}')
print(f'intervalHours: {job5.get("intervalHours","N/A")}')
print(f'whatsappGroup: {job5.get("whatsappGroup","N/A")}')
print(f'enabled: {job5.get("enabled","N/A")}')
print(f'id: {job5.get("id","MISSING")}')
print(f'status: {job5.get("status","MISSING")}')
print(f'lastRunTimestamp: {job5.get("lastRunTimestamp","MISSING")}')
print(f'agentId: {job5.get("agentId","MISSING")}')
print('PROMPT:')
print(job5.get('prompt',''))
