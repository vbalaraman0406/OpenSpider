import requests, json

headers = {'User-Agent': 'OpenSpider Weather Bot (coolvishnu@gmail.com)', 'Accept': 'application/geo+json'}

# Fetch forecast
forecast_resp = requests.get('https://api.weather.gov/gridpoints/PQR/114,109/forecast', headers=headers, timeout=15)
periods = forecast_resp.json()['properties']['periods'][:10]

# Fetch alerts
alerts_resp = requests.get('https://api.weather.gov/alerts/active?point=45.6387,-122.6615', headers=headers, timeout=15)
alerts = alerts_resp.json().get('features', [])

# Build markdown
lines = []
lines.append('# 🌦️ 5-Day Weather Forecast — Vancouver, WA')
lines.append(f'*Source: National Weather Service (NWS)*\n')

if alerts:
    lines.append('## ⚠️ Active Weather Alerts')
    for a in alerts:
        p = a['properties']
        lines.append(f"**{p.get('event','')}** — {p.get('headline','')}")
        lines.append(f"Severity: {p.get('severity','')}")
        lines.append(f"{p.get('description','')[:500]}\n")
else:
    lines.append('## ✅ No Active Weather Alerts\n')

lines.append('| Period | Temp | Conditions | Wind | Precip % | Details |')
lines.append('|--------|------|------------|------|----------|---------|')

for p in periods:
    precip = p.get('probabilityOfPrecipitation', {}).get('value', 'N/A')
    if precip is None:
        precip = 'N/A'
    else:
        precip = f"{precip}%"
    det = p['detailedForecast'][:120]
    lines.append(f"| {p['name']} | {p['temperature']}°{p['temperatureUnit']} | {p['shortForecast']} | {p['windSpeed']} {p['windDirection']} | {precip} | {det} |")

markdown = '\n'.join(lines)

# Also build a compact WhatsApp version
wa = ['🌦️ *Vancouver, WA — 5-Day Forecast*', '']
if alerts:
    wa.append('⚠️ ALERTS:')
    for a in alerts:
        wa.append(f"• {a['properties'].get('event','')}: {a['properties'].get('headline','')}")
    wa.append('')
else:
    wa.append('✅ No active weather alerts\n')

for p in periods:
    precip = p.get('probabilityOfPrecipitation', {}).get('value', 'N/A')
    if precip is None:
        precip = 'N/A'
    else:
        precip = f"{precip}%"
    icon = '☀️' if p['isDaytime'] else '🌙'
    wa.append(f"{icon} *{p['name']}*: {p['temperature']}°{p['temperatureUnit']} — {p['shortForecast']}")
    wa.append(f"   Wind: {p['windSpeed']} {p['windDirection']} | Precip: {precip}")

wa_text = '\n'.join(wa)

with open('/Users/vbalaraman/OpenSpider/weather_email.md', 'w') as f:
    f.write(markdown)
with open('/Users/vbalaraman/OpenSpider/weather_wa.txt', 'w') as f:
    f.write(wa_text)

print('EMAIL_BODY_START')
print(markdown)
print('EMAIL_BODY_END')
print('WA_START')
print(wa_text)
print('WA_END')
