import requests, json

# Step 1: Get forecast URLs from NWS points API
points = requests.get('https://api.weather.gov/points/45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
forecast_url = points['properties']['forecast']
print('Forecast URL:', forecast_url)

# Step 2: Fetch forecast
forecast = requests.get(forecast_url, headers={'User-Agent': 'OpenSpider/1.0'}).json()
periods = forecast['properties']['periods']

# Step 3: Fetch alerts
alerts_data = requests.get('https://api.weather.gov/alerts/active?point=45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
alerts = alerts_data.get('features', [])

# Step 4: Format output
result = {}
result['periods'] = []
for p in periods:
    result['periods'].append({
        'name': p['name'],
        'temp': p['temperature'],
        'tempUnit': p['temperatureUnit'],
        'wind': p['windSpeed'] + ' ' + p['windDirection'],
        'short': p['shortForecast'],
        'detailed': p['detailedForecast'],
        'precip': p.get('probabilityOfPrecipitation', {}).get('value'),
        'isDaytime': p['isDaytime']
    })

result['alerts'] = []
for a in alerts:
    props = a['properties']
    result['alerts'].append({
        'event': props.get('event',''),
        'headline': props.get('headline',''),
        'severity': props.get('severity',''),
        'description': props.get('description','')[:300]
    })

print(json.dumps(result, indent=2))
