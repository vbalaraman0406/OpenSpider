import requests
import json

try:
    resp = requests.get('https://wttr.in/Melbourne,Australia?format=j1', headers={'User-Agent': 'curl/7.68.0'}, timeout=15)
    data = resp.json()
    
    cur = data['current_condition'][0]
    print('=== CURRENT CONDITIONS ===')
    print(f"Temp: {cur['temp_C']}C ({cur['temp_F']}F)")
    print(f"Feels Like: {cur['FeelsLikeC']}C")
    print(f"Condition: {cur['weatherDesc'][0]['value']}")
    print(f"Humidity: {cur['humidity']}%")
    print(f"Wind: {cur['windspeedKmph']} km/h {cur['winddir16Point']}")
    print(f"Pressure: {cur['pressure']} mb")
    print(f"UV Index: {cur['uvIndex']}")
    print(f"Visibility: {cur['visibility']} km")
    print(f"Cloud Cover: {cur['cloudcover']}%")
    
    print('\n=== 3-DAY FORECAST ===')
    for day in data['weather'][:3]:
        print(f"\nDate: {day['date']}")
        print(f"  High: {day['maxtempC']}C ({day['maxtempF']}F)")
        print(f"  Low: {day['mintempC']}C ({day['mintempF']}F)")
        print(f"  Avg Temp: {day['avgtempC']}C")
        print(f"  Condition: {day['hourly'][4]['weatherDesc'][0]['value']}")
        print(f"  Sunrise: {day['astronomy'][0]['sunrise']}")
        print(f"  Sunset: {day['astronomy'][0]['sunset']}")
        print(f"  Max Wind: {day['hourly'][4]['windspeedKmph']} km/h")
        print(f"  Chance of Rain: {day['hourly'][4]['chanceofrain']}%")
except Exception as e:
    print(f'Error: {e}')
