import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Try Google search for flight prices
query = 'flights PDX to LAX June 22 2026 round trip business class prices'
url = f'https://www.google.com/search?q={query.replace(" ", "+")}'

try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f'Status: {r.status_code}')
    # Look for flight-related content
    text = r.text
    # Find price patterns like $XXX
    prices = re.findall(r'\$\d{2,4}', text)
    print(f'Prices found: {prices[:20]}')
    # Find airline names
    airlines = []
    for airline in ['Alaska', 'Frontier', 'Delta', 'United', 'American', 'Southwest', 'JetBlue', 'Spirit']:
        if airline.lower() in text.lower():
            airlines.append(airline)
    print(f'Airlines mentioned: {airlines}')
    # Save raw HTML for analysis
    with open('/Users/vbalaraman/OpenSpider/skills/flight_results.html', 'w') as f:
        f.write(text[:50000])
    print('Saved HTML to flight_results.html')
except Exception as e:
    print(f'Error: {e}')

print('Done')
