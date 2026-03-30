import requests
import json

try:
    r = requests.get('https://statsapi.mlb.com/api/v1/schedule?date=2026-03-13&sportId=1', timeout=10)
    data = r.json()
    total = data.get('totalGames', 0)
    print(f'Regular season games on 2026-03-13: {total}')
    if total > 0:
        for d in data.get('dates', []):
            for g in d.get('games', []):
                away = g['teams']['away']['team']['name']
                home = g['teams']['home']['team']['name']
                print(f'  {away} @ {home}')
    else:
        print('No regular season games scheduled.')
except Exception as e:
    print(f'Error: {e}')

try:
    r2 = requests.get('https://statsapi.mlb.com/api/v1/schedule?date=2026-03-13&sportId=1&gameType=S', timeout=10)
    data2 = r2.json()
    st = data2.get('totalGames', 0)
    print(f'Spring Training games on 2026-03-13: {st}')
except Exception as e:
    print(f'ST Error: {e}')
