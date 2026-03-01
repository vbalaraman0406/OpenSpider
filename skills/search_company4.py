import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. Try letsremodel.com/lander
print('=== letsremodel.com/lander ===')
try:
    r = requests.get('https://www.letsremodel.com/lander', headers=headers, timeout=10)
    print(f'Status: {r.status_code}, Length: {len(r.text)}')
    soup = BeautifulSoup(r.text, 'html.parser')
    # Remove script/style
    for s in soup(['script','style']): s.decompose()
    text = soup.get_text(' ', strip=True)[:2000]
    print(f'Text: {text}')
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', r.text)
    print(f'Phones: {phones}')
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', r.text)
    print(f'Emails: {emails}')
except Exception as e:
    print(f'Error: {e}')

# 2. Yelp direct search
print('\n=== Yelp Direct Search ===')
try:
    url = 'https://www.yelp.com/search?find_desc=Let%27s+Remodel&find_loc=Vancouver%2C+WA+98662'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for s in soup(['script','style']): s.decompose()
    text = soup.get_text(' ', strip=True)
    # Look for rating patterns
    if 'remodel' in text.lower():
        # Find relevant section
        idx = text.lower().find('remodel')
        print(f'Yelp snippet: {text[max(0,idx-200):idx+500]}')
    else:
        print(f'No remodel mention. First 500: {text[:500]}')
except Exception as e:
    print(f'Error: {e}')

# 3. Google Maps search
print('\n=== Google Maps Search ===')
try:
    url = "https://www.google.com/maps/search/Let's+Remodel+Vancouver+WA+98662"
    r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    # Extract any phone/address from response
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', r.text)
    print(f'Phones found: {phones[:5]}')
    # Look for address
    addresses = re.findall(r'\d+\s+[A-Z][a-zA-Z\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct|Pl)', r.text)
    print(f'Addresses: {addresses[:5]}')
except Exception as e:
    print(f'Error: {e}')

# 4. Try Angi / HomeAdvisor
print('\n=== Angi Search ===')
try:
    url = 'https://www.angi.com/companylist/us/wa/vancouver/bathroom-remodeling.htm'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for s in soup(['script','style']): s.decompose()
    text = soup.get_text(' ', strip=True)
    if 'remodel' in text.lower():
        idx = text.lower().find("let's remodel")
        if idx >= 0:
            print(f'Found! Snippet: {text[max(0,idx-100):idx+500]}')
        else:
            print('No exact match for Let\'s Remodel on Angi')
    else:
        print('No results')
except Exception as e:
    print(f'Error: {e}')

# 5. Try Houzz
print('\n=== Houzz Search ===')
try:
    url = 'https://www.houzz.com/professionals/general-contractor/lets-remodel-pfvwus-pf~1234567890'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')
