import json
import re

with open('./cron_jobs.json', 'r') as f:
    data = json.load(f)

print('TOTAL JOBS IN FILE: ' + str(len(data)))
print()

for i, job in enumerate(data):
    name = job.get('name', 'NO NAME')
    print(str(i) + ': ' + name)

print()
print('=' * 80)
print('SEARCHING FOR MARKET/S&P/NASDAQ RELATED JOBS...')
print('=' * 80)

for job in data:
    name = job.get('name', '')
    job_str = json.dumps(job)
    if 'S&P' in name or 'NASDAQ' in name or 'Market' in name or 'Pre-Market' in name or 's&p' in name.lower() or 'nasdaq' in name.lower():
        print()
        print('JOB NAME: ' + name)
        print('-' * 60)
        prompt = job.get('prompt', job.get('task', job.get('description', 'N/A')))
        print('PROMPT:')
        print(prompt)
        print()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', job_str)
        unique_emails = list(dict.fromkeys(emails))
        print('EMAILS: ' + str(unique_emails))
        print()
