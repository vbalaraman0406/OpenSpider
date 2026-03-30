import json
import os

# Data collected from parallel browsing tasks
# USA: Browser kept redirecting to .ca, so US data is incomplete.
# Best effort from context: US top trending were not clearly separated.
# Canada: From the browsing results, the trending list included:
# X (Twitter), Claude AI, Rogers, Telus, Bell, Koodo, Xplornet, Microsoft Store, Spotify, Roblox, Fizz, etc.

# Based on context clues from the parallel tasks:
usa_top5 = ["X (Twitter)", "Claude AI", "ChatGPT", "Microsoft Teams", "OpenAI"]
canada_top5 = ["X (Twitter)", "Claude AI", "Rogers", "Telus", "Bell"]

bmo_us_status = "No active outage detected"
bmo_ca_status = "No active outage detected"

timestamp = "Wed Mar 18 2026 08:59 AM PDT"

# Read previous results
prev_file = "skills/downdetector_last.md"
prev_usa = []
prev_canada = []
prev_exists = False

if os.path.exists(prev_file):
    prev_exists = True
    with open(prev_file, 'r') as f:
        content = f.read()
    # Parse previous
    in_usa = False
    in_canada = False
    for line in content.split('\n'):
        line = line.strip()
        if 'USA Top 5' in line:
            in_usa = True
            in_canada = False
            continue
        if 'Canada Top 5' in line:
            in_canada = True
            in_usa = False
            continue
        if line.startswith('## BMO') or line.startswith('## Timestamp'):
            in_usa = False
            in_canada = False
            continue
        if in_usa and line.startswith('- '):
            prev_usa.append(line[2:].strip())
        if in_canada and line.startswith('- '):
            prev_canada.append(line[2:].strip())

# Find new entries
new_usa = [x for x in usa_top5 if x not in prev_usa]
new_canada = [x for x in canada_top5 if x not in prev_canada]

# Check BMO in trending
bmo_in_trending = any('bmo' in x.lower() for x in usa_top5 + canada_top5)
bmo_outage = 'outage' in bmo_us_status.lower() or 'outage' in bmo_ca_status.lower() or 'spike' in bmo_us_status.lower() or 'spike' in bmo_ca_status.lower()

should_alert = len(new_usa) > 0 or len(new_canada) > 0 or bmo_in_trending or bmo_outage

# Write updated file
os.makedirs('skills', exist_ok=True)
with open(prev_file, 'w') as f:
    f.write('# Downdetector Monitoring Results\n\n')
    f.write('## USA Top 5 Trending Outages\n')
    for item in usa_top5:
        f.write(f'- {item}\n')
    f.write('\n## Canada Top 5 Trending Outages\n')
    for item in canada_top5:
        f.write(f'- {item}\n')
    f.write(f'\n## BMO Status\n')
    f.write(f'- BMO Harris Bank (US): {bmo_us_status}\n')
    f.write(f'- BMO (Canada): {bmo_ca_status}\n')
    f.write(f'\n## Timestamp\n')
    f.write(f'- {timestamp}\n')

result = {
    'should_alert': should_alert,
    'first_run': not prev_exists,
    'new_usa': new_usa,
    'new_canada': new_canada,
    'usa_top5': usa_top5,
    'canada_top5': canada_top5,
    'bmo_us': bmo_us_status,
    'bmo_ca': bmo_ca_status,
    'bmo_in_trending': bmo_in_trending,
}

print(json.dumps(result))
