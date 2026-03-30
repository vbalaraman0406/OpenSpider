import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

# 1. XOME - Extract property details
print('=== XOME.COM DETAILS ===')
try:
    url = 'https://www.xome.com/realestate/Vancouver-WA'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.select('[class*=property], [class*=listing]')
    print(f'Found {len(cards)} elements')
    # Print first 2000 chars of page text to understand structure
    text = soup.get_text(separator='|', strip=True)
    # Find property-like patterns
    lines = text.split('|')
    for i, line in enumerate(lines[:200]):
        if any(kw in line.lower() for kw in ['bed', 'bath', 'sqft', 'vancouver', '$', 'bd', 'ba']):
            context = '|'.join(lines[max(0,i-2):i+5])
            print(f'Match at {i}: {context[:300]}')
            print('---')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== FORECLOSURE.COM DETAILS ===')
try:
    url = 'https://www.foreclosure.com/search/WA/Vancouver/'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.select('[class*=property], [class*=listing]')
    print(f'Found {len(cards)} elements')
    text = soup.get_text(separator='|', strip=True)
    lines = text.split('|')
    for i, line in enumerate(lines[:300]):
        if any(kw in line.lower() for kw in ['bed', 'bath', 'sqft', 'vancouver', '$', 'bd', 'ba']):
            context = '|'.join(lines[max(0,i-2):i+5])
            print(f'Match at {i}: {context[:300]}')
            print('---')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== HUDHOMESTORE.GOV ===')
try:
    url = 'https://www.hudhomestore.gov/Listing/PropertySearchResult'
    params = {'sState': 'WA', 'sCounty': 'Clark', 'sBed': '5', 'iMaxPrice': '600000'}
    r = requests.get(url, headers=headers, params=params, timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator='|', strip=True)[:1000]
        print(text[:1000])
except Exception as e:
    print(f'Error: {e}')
