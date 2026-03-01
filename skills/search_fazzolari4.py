import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. Yelp search
print('=== YELP SEARCH ===')
try:
    url = 'https://www.yelp.com/search?find_desc=Fazzolari&find_loc=Vancouver%2C+WA+98662'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'Yelp status: {r.status_code}')
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for business names
    for tag in soup.find_all(['a','h3','h4','span'], string=re.compile('fazzolari', re.I)):
        print(f'Found: {tag.name} -> {tag.get_text(strip=True)}')
        if tag.get('href'):
            print(f'  Link: {tag["href"]}')
except Exception as e:
    print(f'Yelp error: {e}')

# 2. WA State Contractor License Lookup
print('\n=== WA STATE LICENSE LOOKUP ===')
try:
    url = 'https://secure.lni.wa.gov/verify/Results.aspx'
    # Try GET with params
    params = {'Uession': '', 'SAession': '', 'Session': '', 'ESSION': ''}
    search_url = f'https://secure.lni.wa.gov/verify/'
    r = requests.get(search_url, headers=headers, timeout=15)
    print(f'LNI status: {r.status_code}')
    # Try the API-style search
    api_url = 'https://secure.lni.wa.gov/verify/api/Search'
    payload = {'BusinessName': 'Fazzolari', 'City': 'Vancouver', 'State': 'WA'}
    r2 = requests.get(api_url, params=payload, headers=headers, timeout=15)
    print(f'LNI API status: {r2.status_code}')
    if r2.status_code == 200:
        text = r2.text[:2000]
        if 'fazzolari' in text.lower():
            print('FOUND fazzolari in LNI results!')
            print(text[:1500])
        else:
            print(f'No fazzolari in response. First 500 chars: {text[:500]}')
except Exception as e:
    print(f'LNI error: {e}')

# 3. Google with alternate spellings
print('\n=== GOOGLE ALTERNATE SPELLINGS ===')
queries = [
    'Fazzolari Construction Vancouver WA',
    'Fazzolari Remodeling Vancouver WA',
    'Fazolari contractor Vancouver WA',
    'Fazzolari home improvement Vancouver WA',
    'Fazzolari plumbing Vancouver WA'
]
for q in queries:
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(q)}&num=5'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text().lower()
        if 'fazzolari' in text or 'fazolari' in text:
            print(f'Query "{q}": FOUND match')
            # Extract snippets
            for div in soup.find_all('div'):
                t = div.get_text()
                if 'fazzolari' in t.lower() or 'fazolari' in t.lower():
                    if 20 < len(t) < 300:
                        print(f'  Snippet: {t.strip()}')
        else:
            print(f'Query "{q}": No match')
    except Exception as e:
        print(f'Query "{q}": Error - {e}')

# 4. Try Angi / HomeAdvisor
print('\n=== ANGI SEARCH ===')
try:
    url = 'https://www.angi.com/companylist/us/wa/vancouver/bathroom-remodeling.htm'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'Angi status: {r.status_code}')
    if 'fazzolari' in r.text.lower():
        print('FOUND fazzolari on Angi!')
    else:
        print('No fazzolari on Angi page')
except Exception as e:
    print(f'Angi error: {e}')
