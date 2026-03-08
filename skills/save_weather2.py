import requests, json

points = requests.get('https://api.weather.gov/points/45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
forecast_url = points['properties']['forecast']
forecast = requests.get(forecast_url, headers={'User-Agent': 'OpenSpider/1.0'}).json()
periods = forecast['properties']['periods']
alerts_data = requests.get('https://api.weather.gov/alerts/active?point=45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
alerts = alerts_data.get('features', [])

def get_emoji(short):
    s = short.lower()
    if 'sunny' in s or 'clear' in s: return '☀️'
    if 'partly' in s: return '⛅'
    if 'cloudy' in s or 'cloud' in s: return '☁️'
    if 'rain' in s or 'shower' in s: return '🌧️'
    if 'thunder' in s: return '⛈️'
    if 'snow' in s: return '❄️'
    if 'fog' in s: return '🌫️'
    if 'wind' in s: return '💨'
    return '🌡️'

md = '# Vancouver, WA 5-Day Weather Forecast\n'
md += '*Source: National Weather Service (NWS)*\n\n'

if alerts:
    md += '## Active Weather Alerts\n'
    for a in alerts:
        p = a['properties']
        md += '**' + p.get('event','') + '** - ' + p.get('headline','') + '\n\n'
else:
    md += '> No active weather alerts for Vancouver, WA.\n\n'

md += '## Forecast Overview\n\n'
md += '| Period | Temp | Wind | Precip | Conditions |\n'
md += '|--------|------|------|--------|------------|\n'

for p in periods:
    e = get_emoji(p['shortForecast'])
    precip = p.get('probabilityOfPrecipitation',{}).get('value')
    ps = str(precip) + '%' if precip is not None else 'N/A'
    row = '| ' + p['name'] + ' | ' + str(p['temperature']) + 'F | ' + p['windSpeed'] + ' ' + p['windDirection'] + ' | ' + ps + ' | ' + e + ' ' + p['shortForecast'] + ' |'
    md += row + '\n'

md += '\n## Detailed Forecast\n\n'
for p in periods:
    e = get_emoji(p['shortForecast'])
    md += '### ' + e + ' ' + p['name'] + '\n'
    md += p['detailedForecast'] + '\n\n'

with open('weather_forecast.md', 'w') as f:
    f.write(md)

wa = 'Vancouver, WA Weather Forecast\n\n'
if alerts:
    wa += 'ALERTS:\n'
    for a in alerts:
        wa += '- ' + a['properties'].get('event','') + '\n'
    wa += '\n'
else:
    wa += 'No active alerts\n\n'

for p in periods:
    e = get_emoji(p['shortForecast'])
    precip = p.get('probabilityOfPrecipitation',{}).get('value')
    ps = str(precip) + '%' if precip is not None else 'N/A'
    wa += e + ' ' + p['name'] + ': ' + str(p['temperature']) + 'F, ' + p['shortForecast'] + ', Wind ' + p['windSpeed'] + ' ' + p['windDirection'] + ', Precip ' + ps + '\n'

with open('weather_whatsapp.txt', 'w') as f:
    f.write(wa)

print('DONE')
print('MD length:', len(md))
print('WA length:', len(wa))
