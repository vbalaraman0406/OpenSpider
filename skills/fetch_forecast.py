import requests
import json

url = 'https://api.weather.gov/gridpoints/PQR/100,120/forecast'
headers = {'User-Agent': 'OpenSpider/1.0 (coolvishnu@gmail.com)', 'Accept': 'application/geo+json'}
resp = requests.get(url, headers=headers)
data = resp.json()

periods = data['properties']['periods']
for p in periods:
    pop = p['probabilityOfPrecipitation']['value']
    pop_str = f"{pop}%" if pop is not None else '0%'
    print(f"NAME: {p['name']}")
    print(f"DAYTIME: {p['isDaytime']}")
    print(f"TEMP: {p['temperature']}°{p['temperatureUnit']}")
    print(f"PRECIP: {pop_str}")
    print(f"WIND: {p['windSpeed']} {p['windDirection']}")
    print(f"SHORT: {p['shortForecast']}")
    print(f"DETAIL: {p['detailedForecast']}")
    print('---')
