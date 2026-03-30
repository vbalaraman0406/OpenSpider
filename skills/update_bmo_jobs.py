import json

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

append_text = '\n\nCRITICAL RULE: ONLY send a WhatsApp message to 14156249639@s.whatsapp.net if there is an ACTIVE OUTAGE or ISSUE detected on BMO. If BMO status is normal with NO issues, DO NOT send any message at all. Stay completely silent when there are no problems.'

updated = []
for job in jobs:
    name = (job.get('description', '') + ' ' + job.get('prompt', '') + ' ' + job.get('id', '')).lower()
    if 'bmo' in name:
        if not job['prompt'].endswith(append_text):
            job['prompt'] += append_text
        updated.append(job.get('description', job.get('id')))

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print(f'Updated {len(updated)} BMO jobs: {updated}')
