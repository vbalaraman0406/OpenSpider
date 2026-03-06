import json

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

new_prompt = """You are the F1 Fantasy Team Optimizer. Execute these steps:

1. CHECK RACE CALENDAR: Read the file workspace/f1_calendar_2026.json. Check if any race weekend has a raceDate within the next 4 days from today. If no upcoming race, log 'No upcoming race this week' and stop.

2. FOR THE AUSTRALIAN GP (Round 1, March 8, 2026) AND ALL FUTURE RACES:
   a. Use browse_web to search Google for '[Race Name] FP1 FP2 results lap times [year]' (e.g. 'Australian Grand Prix 2026 FP1 FP2 results lap times').
   b. Read the search results and navigate to F1 official results or reputable sources (formula1.com, autosport.com, motorsport.com).
   c. Extract: top 10 lap times from FP1 and FP2, long-run pace data, tire degradation observations, any reliability issues or red flags.
   d. Compare practice performance against the CURRENT F1 Fantasy team:
      - Current Drivers: Oscar Piastri ($25.5M, TURBO), Carlos Sainz ($11.8M), Oliver Bearman ($7.4M), Isack Hadjar ($15.1M), Sergio Perez ($6.0M)
      - Current Constructors: Ferrari ($23.3M), Aston Martin ($10.3M)
      - Budget remaining: $0.6M
   e. Determine if any swaps are needed based on practice data. Consider:
      - Single-lap pace (qualifying prediction)
      - Long-run pace (race pace prediction)
      - Position gain potential (key for Turbo driver)
      - Reliability concerns (DNF = -15 points)
      - Constructor both-cars-in-points likelihood (+10 bonus)
   f. If changes are recommended, navigate to fantasy.formula1.com using browse_web (user session should be authenticated), go to the team management/edit page, make substitutions (F1 Fantasy allows unlimited free transfers between race weekends), set the optimal Turbo driver, and save the team.
   g. Send an email to coolvishnu@gmail.com with subject '\ud83c\udfce\ufe0f F1 Fantasy Team Updated - [Race Name]' containing:
      - The upcoming race name, date, and circuit
      - FP1 and FP2 results analysis (top 5 drivers, lap times, pace comparison)
      - The updated team lineup with prices and reasoning for any changes
      - Turbo driver selection and why
      - Key risks or alternative picks to watch in FP3
   h. Send the same update summary via send_whatsapp to the user.

3. IMPORTANT TIMING: For the Australian GP, FP1 is at 5:30 PM PST Thursday (Mar 5) and FP2 is at 9:00 PM PST Thursday (Mar 5). FP3 is at 5:30 PM PST Friday (Mar 6). Qualifying locks the Fantasy team at ~9:00 PM PST Friday (Mar 6). Analyze whatever practice data is available at the time this job runs."""

for job in jobs:
    if job.get('id') == 'cron-hc3fjkb7d':
        job['prompt'] = new_prompt.strip()
        job['lastRunTimestamp'] = None  # Force it to fire on next scheduler tick
        job['description'] = 'F1 Fantasy Team Update - Pre-Race Weekend Optimizer'
        print('Updated F1 Fantasy job successfully')
        break

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)
    print('File written successfully')

# Verify
with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    verify = json.load(f)

for job in verify:
    if job.get('id') == 'cron-hc3fjkb7d':
        print(f"\n=== VERIFIED F1 FANTASY JOB ===")
        print(f"ID: {job['id']}")
        print(f"Name: {job['name']}")
        print(f"Status: {job['status']}")
        print(f"Interval: {job['intervalHours']}h")
        print(f"Preferred Time: {job['preferredTime']}")
        print(f"Last Run: {job['lastRunTimestamp']}")
        print(f"Agent: {job['agentId']}")
        print(f"Prompt length: {len(job['prompt'])} chars")
        print(f"Prompt starts with: {job['prompt'][:100]}...")
        print(f"Prompt ends with: ...{job['prompt'][-100:]}")
        break

print(f"\nTotal jobs in file: {len(verify)}")
for j in verify:
    print(f"  - {j.get('id')}: {j.get('name', j.get('description',''))[:60]}")
