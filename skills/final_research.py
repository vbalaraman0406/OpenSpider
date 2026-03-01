import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get services page
print('=== SERVICES ===')
try:
    resp = requests.get('https://www.mountainwoodhomes.com/services/', headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Look for service headings
    for tag in soup.find_all(['h1','h2','h3','h4','a']):
        txt = tag.get_text(strip=True)
        if txt and len(txt) > 3 and len(txt) < 100:
            href = tag.get('href', '')
            if any(kw in txt.lower() for kw in ['remodel', 'kitchen', 'bath', 'addition', 'whole', 'design', 'build', 'outdoor', 'basement', 'adu', 'aging', 'universal', 'custom', 'renovation', 'service']):
                print(f'  - {txt}')
except Exception as e:
    print(f'  Error: {e}')

# Try Houzz for rating
print('\n=== HOUZZ SEARCH ===')
try:
    resp2 = requests.get('https://www.google.com/search?q=site:houzz.com+%22Mountainwood+Homes%22+reviews', headers=headers, timeout=10)
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    text2 = soup2.get_text(separator='\n', strip=True)
    for line in text2.split('\n'):
        line = line.strip()
        if 'mountainwood' in line.lower() and len(line) > 10 and len(line) < 300:
            print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# Try Yelp search
print('\n=== YELP SEARCH ===')
try:
    resp3 = requests.get('https://www.google.com/search?q=site:yelp.com+%22Mountainwood+Homes%22', headers=headers, timeout=10)
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    text3 = soup3.get_text(separator='\n', strip=True)
    found = False
    for line in text3.split('\n'):
        line = line.strip()
        if 'mountainwood' in line.lower() and len(line) > 5 and len(line) < 300:
            print(f'  {line}')
            found = True
    if not found:
        print('  No Yelp listing found')
except Exception as e:
    print(f'  Error: {e}')

# Try BBB search
print('\n=== BBB SEARCH ===')
try:
    resp4 = requests.get('https://www.google.com/search?q=site:bbb.org+%22Mountainwood+Homes%22+Portland', headers=headers, timeout=10)
    soup4 = BeautifulSoup(resp4.text, 'html.parser')
    text4 = soup4.get_text(separator='\n', strip=True)
    found = False
    for line in text4.split('\n'):
        line = line.strip()
        if 'mountainwood' in line.lower() and len(line) > 5 and len(line) < 300:
            print(f'  {line}')
            found = True
    if not found:
        print('  No BBB listing found in search')
except Exception as e:
    print(f'  Error: {e}')

# Try Google Maps rating
print('\n=== GOOGLE MAPS SEARCH ===')
try:
    resp5 = requests.get('https://www.google.com/search?q=Mountainwood+Homes+Tigard+OR+Google+reviews+rating', headers=headers, timeout=10)
    soup5 = BeautifulSoup(resp5.text, 'html.parser')
    text5 = soup5.get_text(separator='\n', strip=True)
    for line in text5.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['rating', 'review', 'star', 'out of 5', '4.', '5.0']):
            if 'mountainwood' in line.lower() or len(line) < 80:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# GuildQuality recommendation rate
print('\n=== GUILDQUALITY SUMMARY ===')
print('  366 verified reviews')
print('  342 of 360 would recommend (95% recommendation rate)')
print('  Source: https://www.guildquality.com/pro/mountainwood-homes')
