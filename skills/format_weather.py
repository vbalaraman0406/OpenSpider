import requests, json

points = requests.get('https://api.weather.gov/points/45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
forecast_url = points['properties']['forecast']
forecast = requests.get(forecast_url, headers={'User-Agent': 'OpenSpider/1.0'}).json()
periods = forecast['properties']['periods']
alerts_data = requests.get('https://api.weather.gov/alerts/active?point=45.6387,-122.6615', headers={'User-Agent': 'OpenSpider/1.0'}).json()
alerts = alerts_data.get('features', [])

emoji_map = {'Sunny':'☀️','Clear':'🌙','Mostly Sunny':'🌤️','Partly Sunny':'⛅','Mostly Cloudy':'🌥️','Cloudy':'☁️','Rain':'🌧️','Light Rain':'🌦️','Heavy Rain':'🌧️','Showers':'🌦️','Thunderstorm':'⛈️','Snow':'❄️','Fog':'🌫️','Wind':'💨','Partly Cloudy':'⛅','Rain Showers':'🌦️','Chance Rain Showers':'🌦️','Rain Showers Likely':'🌦️','Light Rain Likely':'🌦️','Slight Chance Rain Showers':'🌦️','Rain Likely':'🌧️','Chance Light Rain':'🌦️'}

def get_emoji(short):
    for k,v in emoji_map.items():
        if k.lower() in short.lower():
            return v
    return '🌡️'

md = '# 🌦️ Vancouver, WA — 5-Day Weather Forecast\n'
md += '*Source: National Weather Service (NWS)*\n\n'

if alerts:
    md += '## ⚠️ Active Weather Alerts\n'
    for a in alerts:
        p = a['properties']
        md += f"**{p.get('event','')}** — {p.get('headline','')}\n\n"
else:
    md += '> ✅ **No active weather alerts for Vancouver, WA.**\n\n'

md += '## 📊 Forecast Overview\n\n'
md += '| Period | Temp | Wind | Precip % | Conditions |\n'
md += '|--------|------|------|----------|------------|\n'

for p in periods:
    e = get_emoji(p['shortForecast'])
    precip = p.get('probabilityOfPrecipitation',{}).get('value')
    precip_str = f"{precip}%" if precip is not None else 'N/A'
    md += f"| {p['name']} | {p['temperature']}°{p['temperatureUnit']} | {p['windSpeed']} {p['windDirection']} | {precip_str} | {e} {p['shortForecast']} |\n"

md += '\n## 📝 Detailed Forecast\n\n'
for p in periods:
    e = get_emoji(p['shortForecast'])
    md += f"### {e} {p['name']}\n"
    md += f"{p['detailedForecast']}\n\n"

print(md)
