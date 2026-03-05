import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Fetch RotoWire lineups
r = requests.get('https://www.rotowire.com/baseball/daily-lineups.php', headers=headers, timeout=15)
html = r.text

# Extract team abbreviations
team_abbrs = re.findall(r'<div[^>]*class="[^"]*lineup__abbr[^"]*"[^>]*>([A-Z]{2,3})</div>', html)
print(f'Team abbreviations: {team_abbrs}')

# Extract matchup blocks - look for team names in links
team_links = re.findall(r'/baseball/[^"]*team[^"]*">([^<]+)<', html)
print(f'Team links: {team_links[:20]}')

# Try alt pattern for teams
alt_teams = re.findall(r'alt="([A-Z][a-z]+ ?[A-Za-z]*)"', html)
print(f'Alt teams: {alt_teams[:20]}')

# Get all img alt texts (team logos)
logos = re.findall(r'<img[^>]*alt="([^"]+)"[^>]*class="[^"]*logo', html)
print(f'Logo alts: {logos[:20]}')

# Try to find team names near lineup sections
team_names = re.findall(r'lineup__team[^>]*>.*?<(?:a|span|div)[^>]*>([A-Z][^<]{2,25})<', html, re.DOTALL)
print(f'Team names: {team_names[:20]}')

# Weather page - get full game weather details
r3 = requests.get('https://www.rotowire.com/baseball/weather.php', headers=headers, timeout=15)
whtml = r3.text

# Extract weather descriptions with temperature and precipitation
weather_descs = re.findall(r"It's expected to be (\d+).*?F with a (\d+)% chance of precipitation.*?and (\d+) MPH wind", whtml)
print(f'\nWeather details (temp, precip%, wind):')
for w in weather_descs:
    print(f'  Temp: {w[0]}F, Precip: {w[1]}%, Wind: {w[2]} MPH')

# Get venue/city info
venues = re.findall(r'weather__venue[^>]*>([^<]+)<', whtml)
cities = re.findall(r'weather__city[^>]*>([^<]+)<', whtml)
print(f'\nVenues: {venues}')
print(f'Cities: {cities}')

# Get team matchups from weather page
weather_teams = re.findall(r'weather__team[^>]*>([^<]+)<', whtml)
print(f'Weather teams: {weather_teams[:20]}')

# Get all weather card content
weather_blocks = re.findall(r'<div[^>]*class="[^"]*weather__(?:precip|temp|wind)[^"]*"[^>]*>([^<]+)<', whtml)
print(f'Weather blocks: {weather_blocks[:20]}')
