import requests
import json
from datetime import datetime

# Open-Meteo API - free, no key needed
url = 'https://api.open-meteo.com/v1/forecast'
params = {
    'latitude': -37.8136,
    'longitude': 144.9631,
    'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m',
    'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
    'timezone': 'Australia/Melbourne',
    'forecast_days': 3
}

resp = requests.get(url, params=params, timeout=15)
data = resp.json()

c = data['current']
d = data['daily']

wmo_codes = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Foggy', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
    61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
    80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
}

condition = wmo_codes.get(c['weather_code'], f"Code {c['weather_code']}")

print(f"CURRENT:")
print(f"Temp: {c['temperature_2m']}C")
print(f"Feels: {c['apparent_temperature']}C")
print(f"Condition: {condition}")
print(f"Humidity: {c['relative_humidity_2m']}%")
print(f"Wind: {c['wind_speed_10m']} km/h")
print()
print('FORECAST:')
for i in range(3):
    date_str = d['time'][i]
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    day_name = dt.strftime('%A %d %b')
    fc = wmo_codes.get(d['weather_code'][i], f"Code {d['weather_code'][i]}")
    print(f"{day_name}: High {d['temperature_2m_max'][i]}C / Low {d['temperature_2m_min'][i]}C - {fc}")
