import urllib.request
import json

url = 'https://wttr.in/Los+Angeles,California?format=j1'
req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())

current = data['current_condition'][0]
temp_f = current['temp_F']
temp_c = current['temp_C']
humidity = current['humidity']
wind_speed = current['windspeedMiles']
wind_dir = current['winddir16Point']
condition = current['weatherDesc'][0]['value']
feels_like_f = current['FeelsLikeF']

print(f'TEMP_F={temp_f}')
print(f'TEMP_C={temp_c}')
print(f'CONDITION={condition}')
print(f'HUMIDITY={humidity}')
print(f'WIND_SPEED={wind_speed}')
print(f'WIND_DIR={wind_dir}')
print(f'FEELS_LIKE_F={feels_like_f}')
