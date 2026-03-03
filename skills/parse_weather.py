import re
import urllib.request
from html.parser import HTMLParser

url = 'https://www.rotowire.com/baseball/weather.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')

# Extract game weather blocks using regex
# Each game block has team names, time, city, temp, precip%, wind
games = []

# Pattern to find each game's weather summary text
# "It's expected to be XX° F with a XX% chance of precipitation/rain and XX MPH wind blowing XXX in CITY at TIME."
pattern = r"(\w[\w\s]+?)\s+at\s+(\w[\w\s]+?)\s+Monday,\s+at\s+(\d+:\d+\s+PM\s+EST).*?It's expected to be (\d+)° F with a (\d+)% chance of (?:precipitation|rain) and (\d+) MPH wind blowing ([\w\s-]+) in ([\w\s]+?) at"

matches = re.findall(pattern, html, re.DOTALL)

for m in matches:
    away = m[0].strip()
    home = m[1].strip()
    time = m[2].strip()
    temp = m[3]
    precip = m[4]
    wind_speed = m[5]
    wind_dir = m[6].strip()
    city = m[7].strip()
    games.append({
        'matchup': f"{away} @ {home}",
        'time': time,
        'city': city,
        'temp_f': int(temp),
        'precip_pct': int(precip),
        'wind': f"{wind_speed} mph {wind_dir}",
        'risk': '🔴 HIGH' if int(precip) > 50 else ('🟡 MODERATE' if int(precip) > 25 else '🟢 LOW')
    })

# Sort by precip risk (highest first)
games.sort(key=lambda x: x['precip_pct'], reverse=True)

print(f"Found {len(games)} games with weather data:\n")
for g in games:
    print(f"| {g['matchup']} | {g['time']} | {g['city']} | {g['temp_f']}°F | {g['precip_pct']}% | {g['wind']} | {g['risk']} |")

if not games:
    print("No games found via regex. Trying alternative parse...")
    # Try simpler extraction
    blocks = re.findall(r"It's expected to be (\d+)° F with a (\d+)% chance of (?:precipitation|rain) and (\d+) MPH wind blowing ([\w\s-]+) in ([\w\s]+?) at ([\d:]+\s+PM\s+EST)", html)
    for b in blocks:
        print(f"City: {b[4].strip()}, Temp: {b[0]}°F, Precip: {b[1]}%, Wind: {b[2]} mph {b[3].strip()}, Time: {b[5]}")
