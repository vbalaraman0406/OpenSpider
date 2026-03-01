import urllib.request
import urllib.parse
import json
import re

# Try wttr.in which is a simple weather API
try:
    # First try to get location from IP
    ip_req = urllib.request.Request('https://ipinfo.io/json', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(ip_req, timeout=10) as resp:
        ip_data = json.loads(resp.read().decode())
        city = ip_data.get('city', 'New York')
        region = ip_data.get('region', '')
        country = ip_data.get('country', '')
        loc = ip_data.get('loc', '')
        print(f"Detected location: {city}, {region}, {country}")
except Exception as e:
    city = 'New York'
    region = 'New York'
    country = 'US'
    print(f"Could not detect location ({e}), defaulting to {city}")

# Get weather from wttr.in
try:
    weather_url = f'https://wttr.in/{urllib.parse.quote(city)}?format=j1'
    req = urllib.request.Request(weather_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    
    current = data.get('current_condition', [{}])[0]
    area = data.get('nearest_area', [{}])[0]
    
    area_name = area.get('areaName', [{}])[0].get('value', city)
    region_name = area.get('region', [{}])[0].get('value', region)
    country_name = area.get('country', [{}])[0].get('value', country)
    
    temp_f = current.get('temp_F', 'N/A')
    temp_c = current.get('temp_C', 'N/A')
    feels_like_f = current.get('FeelsLikeF', 'N/A')
    feels_like_c = current.get('FeelsLikeC', 'N/A')
    humidity = current.get('humidity', 'N/A')
    desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
    wind_mph = current.get('windspeedMiles', 'N/A')
    wind_dir = current.get('winddir16Point', 'N/A')
    pressure = current.get('pressure', 'N/A')
    visibility = current.get('visibility', 'N/A')
    uv_index = current.get('uvIndex', 'N/A')
    precip = current.get('precipMM', 'N/A')
    cloud_cover = current.get('cloudcover', 'N/A')
    obs_time = current.get('observation_time', 'N/A')
    
    # Get forecast
    forecast_days = data.get('weather', [])
    forecast_info = []
    for day in forecast_days[:3]:
        date = day.get('date', '')
        max_f = day.get('maxtempF', '')
        min_f = day.get('mintempF', '')
        max_c = day.get('maxtempC', '')
        min_c = day.get('mintempC', '')
        avg_desc = day.get('hourly', [{}])[4].get('weatherDesc', [{}])[0].get('value', 'N/A') if len(day.get('hourly', [])) > 4 else 'N/A'
        sunrise = day.get('astronomy', [{}])[0].get('sunrise', '') if day.get('astronomy') else ''
        sunset = day.get('astronomy', [{}])[0].get('sunset', '') if day.get('astronomy') else ''
        forecast_info.append({
            'date': date, 'max_f': max_f, 'min_f': min_f,
            'max_c': max_c, 'min_c': min_c, 'desc': avg_desc,
            'sunrise': sunrise, 'sunset': sunset
        })
    
    print(f"\n=== WEATHER DATA ===")
    print(f"LOCATION: {area_name}, {region_name}, {country_name}")
    print(f"OBS_TIME: {obs_time}")
    print(f"TEMP_F: {temp_f}")
    print(f"TEMP_C: {temp_c}")
    print(f"FEELS_F: {feels_like_f}")
    print(f"FEELS_C: {feels_like_c}")
    print(f"CONDITION: {desc}")
    print(f"HUMIDITY: {humidity}%")
    print(f"WIND: {wind_mph} mph {wind_dir}")
    print(f"PRESSURE: {pressure} mb")
    print(f"VISIBILITY: {visibility} miles")
    print(f"UV_INDEX: {uv_index}")
    print(f"PRECIP: {precip} mm")
    print(f"CLOUD: {cloud_cover}%")
    
    print(f"\n=== FORECAST ===")
    for f in forecast_info:
        print(f"DATE: {f['date']} | HIGH: {f['max_f']}F/{f['max_c']}C | LOW: {f['min_f']}F/{f['min_c']}C | {f['desc']} | Sunrise: {f['sunrise']} | Sunset: {f['sunset']}")

except Exception as e:
    print(f"Error fetching weather: {e}")
    import traceback
    traceback.print_exc()
