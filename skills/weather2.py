import requests
import json
from datetime import datetime

try:
    url = 'https://api.open-meteo.com/v1/forecast?latitude=-37.8136&longitude=144.9631&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,surface_pressure,cloud_cover,uv_index&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max,wind_speed_10m_max&timezone=Australia%2FMelbourne&forecast_days=3'
    resp = requests.get(url, timeout=15)
    data = resp.json()
    
    cur = data['current']
    print('=== CURRENT CONDITIONS ===')
    print(f"Temp: {cur['temperature_2m']}C")
    print(f"Feels Like: {cur['apparent_temperature']}C")
    print(f"Humidity: {cur['relative_humidity_2m']}%")
    print(f"Wind: {cur['wind_speed_10m']} km/h, Dir: {cur['wind_direction_10m']}deg")
    print(f"Pressure: {cur['surface_pressure']} hPa")
    print(f"Cloud Cover: {cur['cloud_cover']}%")
    print(f"UV Index: {cur['uv_index']}")
    print(f"Weather Code: {cur['weather_code']}")
    
    # Weather code mapping
    wmo = {0:'Clear sky',1:'Mainly clear',2:'Partly cloudy',3:'Overcast',45:'Foggy',48:'Rime fog',51:'Light drizzle',53:'Moderate drizzle',55:'Dense drizzle',61:'Slight rain',63:'Moderate rain',65:'Heavy rain',71:'Slight snow',73:'Moderate snow',75:'Heavy snow',80:'Slight showers',81:'Moderate showers',82:'Violent showers',95:'Thunderstorm',96:'Thunderstorm w/ hail',99:'Thunderstorm w/ heavy hail'}
    print(f"Condition: {wmo.get(cur['weather_code'], 'Unknown')}")
    
    daily = data['daily']
    print('\n=== 3-DAY FORECAST ===')
    for i in range(3):
        print(f"\nDate: {daily['time'][i]}")
        print(f"  High: {daily['temperature_2m_max'][i]}C")
        print(f"  Low: {daily['temperature_2m_min'][i]}C")
        print(f"  Condition: {wmo.get(daily['weather_code'][i], 'Unknown')}")
        print(f"  Sunrise: {daily['sunrise'][i]}")
        print(f"  Sunset: {daily['sunset'][i]}")
        print(f"  Max Wind: {daily['wind_speed_10m_max'][i]} km/h")
        print(f"  Rain Chance: {daily['precipitation_probability_max'][i]}%")
except Exception as e:
    print(f'Error: {e}')
