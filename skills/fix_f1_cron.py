import json, time, random, string

path = '/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json'

with open(path, 'r') as f:
    jobs = json.load(f)

# Check if any F1 job exists
f1_exists = any('F1' in j.get('name', '') or 'f1' in j.get('name', '').lower() or 'Fantasy' in j.get('name', '') for j in jobs)
print(f'F1 job exists: {f1_exists}')
print(f'Total jobs: {len(jobs)}')
for j in jobs:
    print(f'  - {j.get("id", "NO_ID")}: {j.get("name", "NO_NAME")}')

if not f1_exists:
    job_id = 'cron-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    new_job = {
        "id": job_id,
        "name": "F1 Fantasy Team Update - Pre-Race Weekend Optimizer",
        "status": "enabled",
        "intervalHours": 24,
        "preferredTime": "09:00",
        "lastRunTimestamp": None,
        "agentId": "agent-worker-01",
        "createdAt": int(time.time() * 1000),
        "prompt": "This is the F1 Fantasy weekly team optimizer. Follow these steps:\n\n1. Read the file workspace/f1_calendar_2026.json to check if there is a race weekend coming up in the next 3 days.\n2. If NO race weekend is coming up in the next 3 days, do nothing - just log 'No upcoming race this week' and stop.\n3. If a race weekend IS coming up in the next 3 days:\n   a. Search the web for the latest F1 practice session results, lap times, and car performance data for the upcoming Grand Prix.\n   b. Search for any driver injuries, grid penalties, car upgrades, or team orders that could affect performance.\n   c. Search for current F1 Fantasy driver and constructor prices on fantasy.formula1.com.\n   d. Based on practice data, current form, price changes, and budget constraints ($100M cap), determine the optimal 5 drivers + 2 constructors lineup and which driver should be Turbo (Boost 2x).\n   e. Navigate to fantasy.formula1.com using browse_web, log in if needed (use wait_for_user for authentication), and update the team:\n      - Go to the team management/edit page\n      - Make substitutions as needed (F1 Fantasy allows unlimited free transfers between race weekends)\n      - Set the optimal Turbo driver\n      - Save the team\n   f. Send an email to coolvishnu@gmail.com with subject '🏎️ F1 Fantasy Team Updated - [Race Name]' containing:\n      - The upcoming race name, date, and circuit\n      - Practice session analysis summary\n      - The updated team lineup with prices and reasoning\n      - Turbo driver selection and why\n      - Any key risks or alternative picks\n   g. Send the same update via send_whatsapp to the user."
    }
    jobs.append(new_job)
    with open(path, 'w') as f:
        json.dump(jobs, f, indent=2)
    print(f'\nINSERTED F1 Fantasy cron job: {job_id}')
    print(f'Total jobs now: {len(jobs)}')
else:
    print('F1 job already exists, skipping insert.')
