import urllib.request
import json
import ssl

# Disable SSL verification for simplicity
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    # Use wttr.in JSON API for Tokyo weather
    url = 'https://wttr.in/Tokyo?format=j1'
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
    response = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.loads(response.read().decode('utf-8'))
    
    current = data['current_condition'][0]
    
    temp_c = current['temp_C']
    temp_f = current['temp_F']
    humidity = current['humidity']
    wind_speed_kmph = current['windspeedKmph']
    wind_speed_mph = current['windspeedMiles']
    wind_dir = current['winddir16Point']
    weather_desc = current['weatherDesc'][0]['value']
    feels_like_c = current['FeelsLikeC']
    feels_like_f = current['FeelsLikeF']
    pressure = current['pressure']
    visibility = current['visibility']
    uv_index = current['uvIndex']
    
    print('='*50)
    print('CURRENT WEATHER IN TOKYO, JAPAN')
    print('='*50)
    print(f'Conditions: {weather_desc}')
    print(f'Temperature: {temp_c}°C / {temp_f}°F')
    print(f'Feels Like: {feels_like_c}°C / {feels_like_f}°F')
    print(f'Humidity: {humidity}%')
    print(f'Wind: {wind_speed_kmph} km/h ({wind_speed_mph} mph) {wind_dir}')
    print(f'Pressure: {pressure} mb')
    print(f'Visibility: {visibility} km')
    print(f'UV Index: {uv_index}')
    print('='*50)
    
    # Save results to a file for later use
    result = {
        'location': 'Tokyo, Japan',
        'conditions': weather_desc,
        'temperature_c': temp_c,
        'temperature_f': temp_f,
        'feels_like_c': feels_like_c,
        'feels_like_f': feels_like_f,
        'humidity': humidity,
        'wind_speed_kmph': wind_speed_kmph,
        'wind_speed_mph': wind_speed_mph,
        'wind_direction': wind_dir,
        'pressure_mb': pressure,
        'visibility_km': visibility,
        'uv_index': uv_index
    }
    
    with open('tokyo_weather.json', 'w') as f:
        json.dump(result, f, indent=2)
    print('\nWeather data saved to tokyo_weather.json')
    
except Exception as e:
    print(f'Error fetching weather: {e}')
    # Fallback: try a simpler format
    try:
        url2 = 'https://wttr.in/Tokyo?format=%C+%t+%h+%w'
        req2 = urllib.request.Request(url2, headers={'User-Agent': 'curl/7.68.0'})
        response2 = urllib.request.urlopen(req2, context=ctx, timeout=15)
        print('Fallback weather info:')
        print(response2.read().decode('utf-8'))
    except Exception as e2:
        print(f'Fallback also failed: {e2}')
