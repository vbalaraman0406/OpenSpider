import urllib.request
import json

try:
    url = 'https://wttr.in/Vancouver+WA+98662?format=j1'
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.64.1'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    
    cur = data['current_condition'][0]
    temp_f = cur.get('temp_F', 'N/A')
    condition = cur.get('weatherDesc', [{}])[0].get('value', 'N/A')
    humidity = cur.get('humidity', 'N/A')
    wind_mph = cur.get('windspeedMiles', 'N/A')
    wind_dir = cur.get('winddir16Point', 'N/A')
    feels_like = cur.get('FeelsLikeF', 'N/A')
    pressure = cur.get('pressure', 'N/A')
    visibility = cur.get('visibilityMiles', 'N/A')
    uv = cur.get('uvIndex', 'N/A')
    
    print(f'CURRENT CONDITIONS:')
    print(f'Temperature: {temp_f}°F')
    print(f'Feels Like: {feels_like}°F')
    print(f'Condition: {condition}')
    print(f'Humidity: {humidity}%')
    print(f'Wind: {wind_mph} mph {wind_dir}')
    print(f'Pressure: {pressure} mb')
    print(f'Visibility: {visibility} miles')
    print(f'UV Index: {uv}')
    
    # Today and tomorrow forecast
    weather = data.get('weather', [])
    for i, day in enumerate(weather[:2]):
        label = 'TODAY' if i == 0 else 'TOMORROW'
        date = day.get('date', 'N/A')
        max_f = day.get('maxtempF', 'N/A')
        min_f = day.get('mintempF', 'N/A')
        avg_humidity = day.get('hourly', [{}])[4].get('humidity', 'N/A') if len(day.get('hourly', [])) > 4 else 'N/A'
        sunrise = day.get('astronomy', [{}])[0].get('sunrise', 'N/A')
        sunset = day.get('astronomy', [{}])[0].get('sunset', 'N/A')
        
        # Get hourly descriptions for forecast summary
        hourly = day.get('hourly', [])
        conditions = []
        for h in hourly:
            desc = h.get('weatherDesc', [{}])[0].get('value', '')
            if desc and desc not in conditions:
                conditions.append(desc)
        
        print(f'\n{label} ({date}):')
        print(f'High: {max_f}°F | Low: {min_f}°F')
        print(f'Sunrise: {sunrise} | Sunset: {sunset}')
        print(f'Conditions: {", ".join(conditions)}')
        
        # Chance of rain
        rain_chances = [h.get('chanceofrain', '0') for h in hourly]
        max_rain = max([int(r) for r in rain_chances]) if rain_chances else 0
        print(f'Max Chance of Rain: {max_rain}%')

except Exception as e:
    print(f'Error: {e}')
