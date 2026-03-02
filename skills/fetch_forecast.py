import urllib.request
from html.parser import HTMLParser
import re

url = 'https://forecast.weather.gov/MapClick.php?CityName=Vancouver&state=WA&site=PQR&textField1=45.6387&textField2=-122.6615'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

# Extract the 7-day forecast tombstone section
import re

# Get forecast icons/periods from tombstone
periods = re.findall(r'<p class="period-name">(.*?)</p>', html, re.DOTALL)
short_desc = re.findall(r'<p class="short-desc">(.*?)</p>', html, re.DOTALL)
temps = re.findall(r'<p class="temp temp-(high|low)">(.*?)</p>', html, re.DOTALL)

print('=== PERIODS ===')
for i, p in enumerate(periods):
    p_clean = re.sub(r'<.*?>', ' ', p).strip()
    print(f'{i}: {p_clean}')

print('\n=== SHORT DESC ===')
for i, s in enumerate(short_desc):
    s_clean = re.sub(r'<.*?>', ' ', s).strip()
    print(f'{i}: {s_clean}')

print('\n=== TEMPS ===')
for i, t in enumerate(temps):
    print(f'{i}: {t[0]} - {t[1]}')

# Extract detailed forecast
detailed = re.findall(r'<div class="col-sm-10 forecast-text">(.*?)</div>', html, re.DOTALL)
print('\n=== DETAILED FORECAST ===')
for i, d in enumerate(detailed):
    d_clean = re.sub(r'<.*?>', '', d).strip()
    print(f'{i}: {d_clean}')

# Extract alerts
alerts_section = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
print('\n=== ALERTS ===')
if alerts_section:
    for a in alerts_section:
        a_clean = re.sub(r'<.*?>', '', a).strip()
        if a_clean:
            print(a_clean)
else:
    # Try another pattern for hazards
    hazards = re.findall(r'<div[^>]*id="[^"]*hazard[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if hazards:
        for h in hazards:
            h_clean = re.sub(r'<.*?>', '', h).strip()
            if h_clean:
                print(h_clean)
    else:
        # Search for any watches/warnings/advisories text
        alert_matches = re.findall(r'((?:Watch|Warning|Advisory|Alert|Hazard)[^<]{0,200})', html, re.IGNORECASE)
        if alert_matches:
            for m in alert_matches[:5]:
                print(m.strip())
        else:
            print('No active alerts found.')

# Extract precip percentages from icon URLs
precip = re.findall(r'forecast-icon.*?src="[^"]*?(\d+\.png|[^"]*?)"[^>]*alt="([^"]*?)"', html, re.DOTALL)
print('\n=== ICON ALT TEXT ===')
for i, p in enumerate(precip):
    print(f'{i}: {p}')
