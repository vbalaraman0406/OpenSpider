import json
import os

cron_file = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'
if not os.path.exists(cron_file):
    print('cron_jobs.json not found')
    exit(1)

with open(cron_file, 'r') as f:
    cron_data = json.load(f)

updated = False
for job in cron_data:
    if 'Trump Truth Social Monitor' in job.get('description', ''):
        old_prompt = job.get('prompt', '')
        new_prompt = old_prompt + '\n\nUse the logged-in session from workspace/truth_social_session.json to monitor Trump\'s Truth Social feed. Ensure the session file exists and contains valid cookies.'
        job['prompt'] = new_prompt
        print(f"Updated job ID: {job['id']}")
        print(f"New prompt preview: {new_prompt[:150]}...")
        updated = True
        break

if not updated:
    print('Trump Truth Social Monitor job not found in cron_jobs.json')
    exit(1)

with open(cron_file, 'w') as f:
    json.dump(cron_data, f, indent=2)

print('Cron job prompt updated successfully.')