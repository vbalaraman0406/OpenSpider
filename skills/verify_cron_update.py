import json
import os

cron_file = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
if not os.path.exists(cron_file):
    print('ERROR: cron_jobs.json not found')
    exit(1)

with open(cron_file, 'r') as f:
    cron_data = json.load(f)

job_found = False
for job in cron_data:
    if 'Trump Truth Social Monitor' in job.get('description', ''):
        job_found = True
        job_id = job.get('id', 'N/A')
        description = job.get('description', 'N/A')
        interval = job.get('intervalHours', 'N/A')
        prompt = job.get('prompt', '')
        session_in_prompt = 'truth_social_session.json' in prompt
        print(f'Job ID: {job_id}')
        print(f'Description: {description}')
        print(f'Interval: {interval} hours')
        print(f'Prompt includes session reference: {session_in_prompt}')
        print(f'Prompt preview (first 200 chars): {prompt[:200]}...')
        break

if not job_found:
    print('ERROR: Trump Truth Social Monitor job not found')
    exit(1)