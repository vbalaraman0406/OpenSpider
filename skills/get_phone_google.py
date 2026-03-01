import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get contact page for phone number
print('=== CONTACT PAGE ===')
try:
    resp = requests.get('https://www.mountainwoodhomes.com/contact/', headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    # Find phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phones:
        print(f'  Phone numbers found: {set(phones)}')
    # Find address
    for line in text.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['tigard', 'portland', 'vancouver', 'address', 'phone', 'call', 'email']):
            if len(line) < 200:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# Also check the main page for phone
print('\n=== MAIN PAGE PHONE ===')
try:
    resp2 = requests.get('https://www.mountainwoodhomes.com/', headers=headers, timeout=10)
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    text2 = soup2.get_text(separator='\n', strip=True)
    phones2 = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text2)
    if phones2:
        print(f'  Phone numbers found: {set(phones2)}')
    # Check for license info
    for line in text2.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['license', 'ccb', 'bonded', 'insured', 'certified']):
            if len(line) < 200:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# Try Google search for their Google rating
print('\n=== GOOGLE RATING SEARCH ===')
try:
    resp3 = requests.get('https://www.google.com/search?q=%22Mountainwood+Homes%22+Tigard+reviews', headers=headers, timeout=10)
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    text3 = soup3.get_text(separator='\n', strip=True)
    for line in text3.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['rating', 'review', 'star', '/5', 'out of']):
            if len(line) < 150:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# Try Houzz direct
print('\n=== HOUZZ DIRECT ===')
try:
    resp4 = requests.get('https://www.houzz.com/professionals/general-contractor/mountainwood-homes-pfvwus-pf~1513879289', headers=headers, timeout=10)
    soup4 = BeautifulSoup(resp4.text, 'html.parser')
    text4 = soup4.get_text(separator='\n', strip=True)
    for line in text4.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['review', 'rating', 'star', 'recommend']):
            if len(line) < 150 and len(line) > 3:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')
