import json
from datetime import datetime, timedelta

today = datetime(2026, 3, 14)
window = today + timedelta(days=4)

with open('workspace/f1_calendar_2026.json') as f:
    races = json.load(f)

found = False
for r in races:
    rd = datetime.strptime(r['raceDate'], '%Y-%m-%d')
    if today <= rd <= window:
        found = True
        print(f"UPCOMING RACE FOUND:")
        print(f"  Race: {r['raceName']} (Round {r['round']})")
        print(f"  Date: {r['raceDate']}")
        print(f"  Circuit: {r['circuit']}, {r['country']}")

if not found:
    print('No upcoming race this week — stopping.')
    # Show next race for context
    future = [(r, datetime.strptime(r['raceDate'], '%Y-%m-%d')) for r in races if datetime.strptime(r['raceDate'], '%Y-%m-%d') > today]
    if future:
        nxt = min(future, key=lambda x: x[1])
        days_away = (nxt[1] - today).days
        print(f"  Next race: {nxt[0]['raceName']} on {nxt[0]['raceDate']} ({days_away} days away)")
