import json

# Update cron_jobs.json with new timestamp
try:
    with open('workspace/cron_jobs.json', 'r') as f:
        data = json.load(f)
    # Update the last_check timestamp for the first job (Trump Truth Social Monitor)
    data['jobs'][0]['last_check'] = '2026-03-21T13:27:39.300Z'
    with open('workspace/cron_jobs.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('Updated cron_jobs.json with new timestamp: 2026-03-21T13:27:39.300Z')
except Exception as e:
    print(f'Error updating cron_jobs.json: {e}')