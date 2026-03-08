import json

with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

new_prompt = """Search the web for the latest news and developments on the Iran war / US-Iran conflict. Compile a comprehensive update covering military operations, diplomatic developments, regional escalation, economic/market impact (oil prices, gold, stock indices, defense stocks), and humanitarian situation. Write a concise summary of all findings. Send this update as a WhatsApp message to the group 'Stock Market Discussions' using the send_whatsapp tool. ALSO send the same summary via send_whatsapp with the 'to' field set to '+14156905841'."""

for job in data:
    if job.get('id') == 'cron-hckpx7ers':
        job['prompt'] = new_prompt.strip()
        updated_job = job
        break

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Updated job:')
print(json.dumps(updated_job, indent=2))
