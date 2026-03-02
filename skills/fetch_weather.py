import urllib.request
import json
import re

# Fetch NWS API forecast for Vancouver WA
url = 'https://api.weather.gov/gridpoints/PQR/95,68/forecast'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenSpider/1.0'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())

periods = data['properties']['periods']

# Also fetch hourly for more detail
url2 = 'https://api.weather.gov/gridpoints/PQR/95,68/forecast/hourly'
req2 = urllib.request.Request(url2, headers={'User-Agent': 'OpenSpider/1.0'})
resp2 = urllib.request.urlopen(req2)
data2 = json.loads(resp2.read().decode())
hourly = data2['properties']['periods']

# Print the 7-day forecast periods
print('=== 7-DAY FORECAST PERIODS ===')
for p in periods[:14]:  # up to 7 days (day+night)
    print(f"Name: {p['name']}")
    print(f"  Temp: {p['temperature']}°{p['temperatureUnit']}")
    print(f"  Wind: {p['windSpeed']} {p['windDirection']}")
    print(f"  Short: {p['shortForecast']}")
    print(f"  Detail: {p['detailedForecast'][:200]}")
    precip = p.get('probabilityOfPrecipitation', {}).get('value', 'N/A')
    humidity = p.get('relativeHumidity', {}).get('value', 'N/A')
    print(f"  Precip%: {precip}, Humidity%: {humidity}")
    print()

# Get alerts
print('=== ALERTS ===')
alert_url = 'https://api.weather.gov/alerts/active?point=45.6372,-122.6614'
req3 = urllib.request.Request(alert_url, headers={'User-Agent': 'OpenSpider/1.0'})
resp3 = urllib.request.urlopen(req3)
alert_data = json.loads(resp3.read().decode())
features = alert_data.get('features', [])
if features:
    for a in features:
        props = a['properties']
        print(f"Alert: {props['headline']}")
        print(f"  Severity: {props['severity']}")
        print(f"  Description: {props['description'][:200]}")
else:
    print('No active alerts.')

# Print some hourly data for today and tomorrow for morning/afternoon breakdown
print('\n=== HOURLY SAMPLES (first 24h) ===')
for h in hourly[:24]:
    precip = h.get('probabilityOfPrecipitation', {}).get('value', 'N/A')
    humidity = h.get('relativeHumidity', {}).get('value', 'N/A')
    print(f"{h['startTime'][:16]} | {h['temperature']}°F | {h['windSpeed']} {h['windDirection']} | {h['shortForecast']} | Precip:{precip}% | Hum:{humidity}%")
