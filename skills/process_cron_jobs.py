import json
from datetime import datetime

# Define the current date for comparison
current_date_str = '2026-03-09'
current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()

# Load the cron jobs data
with open('cron_jobs.json', 'r') as f:
    jobs = json.load(f)

jobs_run_today = []
jobs_not_run_today = []

for i, job in enumerate(jobs):
    job_id = i + 1  # Simple ID for output
    description = job.get('prompt', 'No description provided')
    last_run_timestamp = job.get('lastRun')

    if last_run_timestamp:
        # Assuming lastRun is in ISO format (e.g., '2026-03-09T10:30:00Z')
        last_run_date = datetime.fromisoformat(last_run_timestamp.replace('Z', '+00:00')).date()
        if last_run_date == current_date:
            jobs_run_today.append({
                'id': job_id,
                'description': description,
                'lastRunTimestamp': last_run_timestamp
            })
        else:
            jobs_not_run_today.append({
                'id': job_id,
                'description': description,
                'lastRunTimestamp': last_run_timestamp
            })
    else:
        jobs_not_run_today.append({
            'id': job_id,
            'description': description,
            'lastRunTimestamp': 'Never run'
        })

output = {
    'jobs_run_today': jobs_run_today,
    'jobs_not_run_today': jobs_not_run_today
}

print(json.dumps(output, indent=2))
