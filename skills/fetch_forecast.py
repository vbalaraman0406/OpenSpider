import json, requests

url = 'https://api.weather.gov/gridpoints/PQR/100,120/forecast'
headers = {'User-Agent': 'OpenSpider/1.0 (weather@openspider.ai)', 'Accept': 'application/geo+json'}
resp = requests.get(url, headers=headers, timeout=15)
data = resp.json()

periods = data['properties']['periods']

# Check for alerts
alerts_url = 'https://api.weather.gov/alerts/active?point=45.6387,-122.6615'
try:
    resp2 = requests.get(alerts_url, headers=headers, timeout=15)
    alerts_data = resp2.json()
    alerts = alerts_data.get('features', [])
    alert_texts = []
    for a in alerts:
        props = a.get('properties', {})
        alert_texts.append(f"{props.get('event','Unknown')}: {props.get('headline','No details')}")
except:
    alert_texts = []

rows = []
for p in periods:
    name = p['name']
    temp = p['temperature']
    unit = p['temperatureUnit']
    is_day = p['isDaytime']
    high_low = f"{'High' if is_day else 'Low'}: {temp}°{unit}"
    precip = p['probabilityOfPrecipitation']['value']
    precip_str = f"{precip}%" if precip is not None else 'N/A'
    wind = f"{p['windSpeed']} {p['windDirection']}"
    short = p['shortForecast']
    detailed = p['detailedForecast']
    rows.append({'name': name, 'high_low': high_low, 'conditions': short, 'precip': precip_str, 'wind': wind, 'detailed': detailed})

# WhatsApp summary
wa_lines = ['🌦️ Vancouver, WA 5-Day Forecast\n']
for r in rows:
    wa_lines.append(f"*{r['name']}*: {r['conditions']}, {r['high_low']}, Precip: {r['precip']}, Wind: {r['wind']}")
if alert_texts:
    wa_lines.append('\n⚠️ ACTIVE ALERTS:')
    for at in alert_texts:
        wa_lines.append(f"  • {at}")
else:
    wa_lines.append('\n✅ No active weather alerts.')
wa_summary = '\n'.join(wa_lines)

# Markdown table for email
alert_cell = '; '.join(alert_texts) if alert_texts else 'None'
md_lines = ['## 🌦️ Vancouver, WA — 5-Day Weather Forecast', '', '*Generated from National Weather Service (weather.gov)*', '']
md_lines.append('| Period | Conditions | High/Low | Precip % | Wind | Alerts |')
md_lines.append('|--------|-----------|----------|----------|------|--------|')
for r in rows:
    md_lines.append(f"| {r['name']} | {r['conditions']} | {r['high_low']} | {r['precip']} | {r['wind']} | {alert_cell} |")
md_lines.append('')
md_lines.append('### Detailed Forecasts')
md_lines.append('')
for r in rows:
    md_lines.append(f"**{r['name']}**: {r['detailed']}\n")
md_table = '\n'.join(md_lines)

output = {'wa_summary': wa_summary, 'md_table': md_table, 'alert_count': len(alert_texts)}
print(json.dumps(output))
