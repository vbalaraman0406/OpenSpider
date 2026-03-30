import json
from datetime import datetime, timedelta

today = datetime(2026, 3, 10)
window_start = today - timedelta(days=4)
window_end = today + timedelta(days=4)

try:
    with open('workspace/f1_calendar_2026.json', 'r') as f:
        calendar = json.load(f)
except FileNotFoundError:
    print('File not found: workspace/f1_calendar_2026.json')
    exit(1)

races = calendar if isinstance(calendar, list) else calendar.get('races', calendar.get('schedule', []))

found = False
for race in races:
    race_date_str = race.get('raceDate', race.get('race_date', race.get('date', '')))
    if not race_date_str:
        continue
    # Try parsing various date formats
    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%B %d, %Y', '%d %B %Y']:
        try:
            race_date = datetime.strptime(race_date_str[:10], fmt) if 'T' in race_date_str else datetime.strptime(race_date_str, fmt)
            break
        except ValueError:
            try:
                race_date = datetime.strptime(race_date_str[:10], '%Y-%m-%d')
                break
            except ValueError:
                continue
    else:
        continue
    
    if window_start <= race_date <= window_end:
        found = True
        print('=== MATCHING RACE FOUND ===')
        for k, v in race.items():
            print(f'  {k}: {v}')
        print()

if not found:
    print('No upcoming race this week')
