import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req, context=ctx, timeout=timeout)
    return json.loads(response.read().decode('utf-8'))

try:
    # Open-Meteo free API - no key needed
    # Tokyo coordinates: 35.6762, 139.6503
    url = ('https://api.open-meteo.com/v1/forecast'
           '?latitude=35.6762&longitude=139.6503'
           '&current=temperature_2m,relative_humidity_2m,apparent_temperature,'
           'weather_code,wind_speed_10m,wind_direction_10m,surface_pressure'
           '&temperature_unit=celsius'
           '&wind_speed_unit=kmh')
    
    data = fetch_url(url)
    current = data['current']
    
    temp_c = current['temperature_2m']
    temp_f = round(temp_c * 9/5 + 32, 1)
    humidity = current['relative_humidity_2m']
    feels_like_c = current['apparent_temperature']
    feels_like_f = round(feels_like_c * 9/5 + 32, 1)
    wind_speed_kmph = current['wind_speed_10m']
    wind_speed_mph = round(wind_speed_kmph * 0.621371, 1)
    wind_dir_deg = current['wind_direction_10m']
    pressure = current['surface_pressure']
    weather_code = current['weather_code']
    
    # WMO Weather interpretation codes
    wmo_codes = {
        0: 'Clear sky',
        1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Foggy', 48: 'Depositing rime fog',
        51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
        56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
        66: 'Light freezing rain', 67: 'Heavy freezing rain',
        71: 'Slight snowfall', 73: 'Moderate snowfall', 75: 'Heavy snowfall',
        77: 'Snow grains',
        80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
        85: 'Slight snow showers', 86: 'Heavy snow showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
    }
    
    # Convert wind direction degrees to compass
    dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    ix = round(wind_dir_deg / 22.5) % 16
    wind_dir_compass = dirs[ix]
    
    conditions = wmo_codes.get(weather_code, f'Unknown (code {weather_code})')
    
    print('='*50)
    print('CURRENT WEATHER IN TOKYO, JAPAN')
    print('='*50)
    print(f'Conditions: {conditions}')
    print(f'Temperature: {temp_c}°C / {temp_f}°F')
    print(f'Feels Like: {feels_like_c}°C / {feels_like_f}°F')
    print(f'Humidity: {humidity}%')
    print(f'Wind: {wind_speed_kmph} km/h ({wind_speed_mph} mph) {wind_dir_compass}')
    print(f'Pressure: {pressure} hPa')
    print('='*50)
    
    result = {
        'location': 'Tokyo, Japan',
        'conditions': conditions,
        'weather_code': weather_code,
        'temperature_c': temp_c,
        'temperature_f': temp_f,
        'feels_like_c': feels_like_c,
        'feels_like_f': feels_like_f,
        'humidity': humidity,
        'wind_speed_kmph': wind_speed_kmph,
        'wind_speed_mph': wind_speed_mph,
        'wind_direction': wind_dir_compass,
        'wind_direction_degrees': wind_dir_deg,
        'pressure_hpa': pressure
    }
    
    with open('tokyo_weather.json', 'w') as f:
        json.dump(result, f, indent=2)
    print('\nWeather data saved to tokyo_weather.json')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
