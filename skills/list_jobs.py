import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

print('Total jobs:', len(jobs))
for j in jobs:
    jid = j.get('id', 'NO_ID')
    name = j.get('name', 'NO_NAME')
    prompt_preview = j.get('prompt', '')[:80]
    print(f'ID: {jid}')
    print(f'  Name: {name}')
    print(f'  Prompt: {prompt_preview}...')
    print()
