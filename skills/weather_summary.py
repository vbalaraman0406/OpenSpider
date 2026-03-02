import urllib.request, json

url = 'https://api.weather.gov/gridpoints/PQR/95,68/forecast'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenSpider/1.0'})
data = json.loads(urllib.request.urlopen(req).read().decode())
periods = data['properties']['periods']

# Print all periods compactly
for p in periods[:12]:
    precip = p.get('probabilityOfPrecipitation',{}).get('value','N/A')
    hum = p.get('relativeHumidity',{}).get('value','N/A')
    det = p['detailedForecast'][:300]
    print(f"{p['name']}|{p['temperature']}|{p['temperatureUnit']}|{p['windSpeed']}|{p['windDirection']}|{p['shortForecast']}|P:{precip}|H:{hum}")
    print(f"  DET:{det}")
    print()

# Alerts
alert_url = 'https://api.weather.gov/alerts/active?point=45.6372,-122.6614'
req3 = urllib.request.Request(alert_url, headers={'User-Agent': 'OpenSpider/1.0'})
alert_data = json.loads(urllib.request.urlopen(req3).read().decode())
features = alert_data.get('features', [])
print(f"ALERTS: {len(features)} active")
for a in features:
    print(f"  {a['properties']['headline']}")

# Get hourly humidity ranges per day
url2 = 'https://api.weather.gov/gridpoints/PQR/95,68/forecast/hourly'
req2 = urllib.request.Request(url2, headers={'User-Agent': 'OpenSpider/1.0'})
data2 = json.loads(urllib.request.urlopen(req2).read().decode())
hourly = data2['properties']['periods']

from collections import defaultdict
day_hum = defaultdict(list)
for h in hourly[:120]:
    date = h['startTime'][:10]
    hum = h.get('relativeHumidity',{}).get('value')
    if hum: day_hum[date].append(hum)

print("\nHUMIDITY BY DATE:")
for d in sorted(day_hum.keys())[:6]:
    vals = day_hum[d]
    print(f"  {d}: min={min(vals)}% max={max(vals)}% avg={sum(vals)//len(vals)}%")
