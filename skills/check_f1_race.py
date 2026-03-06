import json
from datetime import datetime, timedelta

# Try both possible paths
paths = ['workspace/f1_calendar_2026.json', 'skills/f1_calendar_2026.json', '/Users/vbalaraman/OpenSpider/skills/f1_calendar_2026.json', '/Users/vbalaraman/OpenSpider/workspace/f1_calendar_2026.json']

calendar = None
for p in paths:
    try:
        with open(p, 'r') as f:
            calendar = json.load(f)
            print(f'Loaded from: {p}')
            break
    except:
        continue

if not calendar:
    print('FILE_NOT_FOUND')
    exit(1)

today = datetime(2026, 3, 5)
window_end = today + timedelta(days=3)  # March 5-8

print(f'Checking window: {today.strftime("%Y-%m-%d")} to {window_end.strftime("%Y-%m-%d")}')

found = False
for race in calendar:
    sessions = race.get('sessions', {})
    for session_name, session_date_str in sessions.items():
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d')
        if today <= session_date <= window_end:
            print(f'RACE FOUND!')
            print(f'Name: {race["name"]}')
            print(f'Circuit: {race["circuit"]}')
            print(f'Country: {race["country"]}')
            print(f'City: {race.get("city", "N/A")}')
            print(f'Sessions:')
            for sn, sd in sessions.items():
                print(f'  {sn}: {sd}')
            found = True
            break
    if found:
        break

if not found:
    print('NO_RACE_UPCOMING')