import json
import re

with open('./cron_jobs.json', 'r') as f:
    data = json.load(f)

targets = [
    'Daily S&P 500 & NASDAQ Market Snapshot',
    'Pre-Market Morning Brief - S&P 500 & NASDAQ'
]

for job in data:
    name = job.get('name', '')
    if name in targets:
        print('=' * 80)
        print('JOB NAME: ' + name)
        print('=' * 80)
        prompt = job.get('prompt', job.get('task', job.get('description', '')))
        print('FULL PROMPT/TASK TEXT:')
        print(prompt)
        print()
        job_str = json.dumps(job)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', job_str)
        unique_emails = list(dict.fromkeys(emails))
        print('EMAILS FOUND: ' + str(unique_emails))
        print()
