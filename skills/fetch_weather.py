import urllib.request
import json

# NWS API for Vancouver, WA coordinates
url = 'https://api.weather.gov/gridpoints/PQR/100,120/forecast'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenSpider/1.0 (coolvishnu@gmail.com)', 'Accept': 'application/geo+json'})

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode())
    periods = data['properties']['periods']
    
    for p in periods[:14]:  # Get 7 days (day+night)
        print(f"{p['name']}|{p['temperature']}|{p['temperatureUnit']}|{p['windSpeed']}|{p['windDirection']}|{p['shortForecast']}|{p.get('probabilityOfPrecipitation',{}).get('value','N/A')}")
except Exception as e:
    print(f'Error: {e}')
    # Fallback: try the points endpoint first
    url2 = 'https://api.weather.gov/points/45.6372,-122.5965'
    req2 = urllib.request.Request(url2, headers={'User-Agent': 'OpenSpider/1.0', 'Accept': 'application/geo+json'})
    resp2 = urllib.request.urlopen(req2)
    data2 = json.loads(resp2.read().decode())
    forecast_url = data2['properties']['forecast']
    print(f'Forecast URL: {forecast_url}')
    req3 = urllib.request.Request(forecast_url, headers={'User-Agent': 'OpenSpider/1.0', 'Accept': 'application/geo+json'})
    resp3 = urllib.request.urlopen(req3)
    data3 = json.loads(resp3.read().decode())
    periods = data3['properties']['periods']
    for p in periods[:14]:
        print(f"{p['name']}|{p['temperature']}|{p['temperatureUnit']}|{p['windSpeed']}|{p['windDirection']}|{p['shortForecast']}|{p.get('probabilityOfPrecipitation',{}).get('value','N/A')}")
