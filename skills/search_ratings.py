import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get awards page
print('=== AWARDS PAGE ===')
resp = requests.get('https://www.mountainwoodhomes.com/about/awards/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text(separator='\n', strip=True)
lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
for line in lines:
    if any(kw in line.lower() for kw in ['award', 'bbb', 'houzz', 'nari', 'association', 'member', 'certified', 'accredited', 'best', 'winner', 'star', 'rating', 'review', 'yelp', 'google', 'angi']):
        print(f'  {line[:250]}')

# Print all lines from awards page (limited)
print('\n=== ALL AWARDS PAGE CONTENT (first 50 lines) ===')
for i, line in enumerate(lines[:50]):
    print(f'  {line[:200]}')

# Search for Google reviews
print('\n=== SEARCHING GOOGLE REVIEWS ===')
try:
    search_url = 'https://www.google.com/search?q=Mountainwood+Homes+Portland+OR+reviews'
    resp = requests.get(search_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    for line in text.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['review', 'rating', 'star', '4.', '5.', 'out of']):
            if len(line) > 5 and len(line) < 300:
                print(f'  {line}')
except Exception as e:
    print(f'Error: {e}')

# Search Yelp
print('\n=== SEARCHING YELP ===')
try:
    yelp_url = 'https://www.yelp.com/search?find_desc=Mountainwood+Homes&find_loc=Portland%2C+OR'
    resp = requests.get(yelp_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    for line in text.split('\n'):
        line = line.strip()
        if 'mountainwood' in line.lower() or 'review' in line.lower() or 'star' in line.lower():
            if len(line) > 3 and len(line) < 300:
                print(f'  {line}')
except Exception as e:
    print(f'Error: {e}')

# Try BBB
print('\n=== SEARCHING BBB ===')
try:
    bbb_url = 'https://www.bbb.org/search?find_country=US&find_text=Mountainwood+Homes&find_loc=Portland%2C+OR'
    resp = requests.get(bbb_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    for line in text.split('\n'):
        line = line.strip()
        if 'mountainwood' in line.lower() or 'rating' in line.lower() or 'accredited' in line.lower():
            if len(line) > 3 and len(line) < 300:
                print(f'  {line}')
except Exception as e:
    print(f'Error: {e}')

# Try Houzz
print('\n=== SEARCHING HOUZZ ===')
try:
    houzz_url = 'https://www.houzz.com/professionals/general-contractors/mountainwood-homes-pfvwus-pf~1234567890'
    resp = requests.get('https://www.houzz.com/professionals/general-contractors/mountainwood-homes-tigard-or-pfvwus-pf~1234567890', headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
except Exception as e:
    print(f'Error: {e}')
