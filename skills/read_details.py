import json
with open('forecast_data.json','r') as f:
    periods = json.load(f)
for p in periods[:14]:
    pop = p['probabilityOfPrecipitation']['value']
    pop_str = f"{pop}%" if pop is not None else '0%'
    hum = p.get('relativeHumidity',{}).get('value','N/A')
    print(f"{p['name']}|{p['temperature']}F|{pop_str}|{p['windSpeed']} {p['windDirection']}|Hum:{hum}%|{p['detailedForecast'][:200]}")
    print('===')
