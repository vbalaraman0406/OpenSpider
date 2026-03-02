import urllib.request
import json

# Use weather.gov API for grid forecast
url = 'https://api.weather.gov/points/45.6387,-122.6615'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenSpider/1.0'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())

forecast_url = data['properties']['forecast']
print(f'Forecast URL: {forecast_url}')

req2 = urllib.request.Request(forecast_url, headers={'User-Agent': 'OpenSpider/1.0'})
resp2 = urllib.request.urlopen(req2)
forecast = json.loads(resp2.read())

periods = forecast['properties']['periods']
for p in periods[:12]:
    print(f"--- {p['name']} ---")
    print(f"Temp: {p['temperature']}°{p['temperatureUnit']}")
    print(f"Wind: {p['windSpeed']} {p['windDirection']}")
    print(f"Short: {p['shortForecast']}")
    print(f"Detail: {p['detailedForecast']}")
    humidity = p.get('relativeHumidity', {}).get('value', 'N/A') if isinstance(p.get('relativeHumidity'), dict) else 'N/A'
    print(f"Humidity: {humidity}%")
    precip = p.get('probabilityOfPrecipitation', {}).get('value', 'N/A') if isinstance(p.get('probabilityOfPrecipitation'), dict) else 'N/A'
    print(f"Precip%: {precip}")
    print()
