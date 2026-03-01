import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. WA LNI Contractor Search
print('=== WA LNI Contractor Search ===')
try:
    url = 'https://secure.lni.wa.gov/verify/Results.aspx'
    params = {'mode': 'ContractorName', 'ContractorName': 'fazzolari', 'SortColumn': 'ContractorName', 'SortOrder': 'asc'}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    print(f'Status: {r.status_code}')
    soup = BeautifulSoup(r.text, 'html.parser')
    tables = soup.find_all('table')
    for t in tables:
        rows = t.find_all('tr')
        for row in rows[:10]:
            cells = row.find_all(['td','th'])
            text = ' | '.join(c.get_text(strip=True) for c in cells)
            if text.strip():
                print(text)
except Exception as e:
    print(f'Error: {e}')

# 2. Try LNI API-style search
print('\n=== WA LNI API Search ===')
try:
    url2 = 'https://secure.lni.wa.gov/verify/api/contractor'
    params2 = {'contractorName': 'fazzolari'}
    r2 = requests.get(url2, params=params2, headers=headers, timeout=15)
    print(f'Status: {r2.status_code}')
    if r2.status_code == 200:
        try:
            data = r2.json()
            if isinstance(data, list):
                for item in data[:5]:
                    print(item)
            else:
                print(str(data)[:1000])
        except:
            print(r2.text[:1000])
except Exception as e:
    print(f'Error: {e}')

# 3. Google search with curl-like approach
print('\n=== Google Search ===')
try:
    queries = ['Fazzolari+contractor+Vancouver+WA', 'Fazzolari+bathroom+remodel+Vancouver+WA+98662', 'Fazzolari+construction+Vancouver+Washington']
    for q in queries:
        url3 = f'https://www.google.com/search?q={q}&num=10'
        r3 = requests.get(url3, headers=headers, timeout=15)
        soup3 = BeautifulSoup(r3.text, 'html.parser')
        # Extract all links
        links = soup3.find_all('a', href=True)
        found = False
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            if 'fazzolari' in text.lower() or 'fazzolari' in href.lower():
                print(f'FOUND: {text} -> {href}')
                found = True
        if not found:
            # Check full text
            full = soup3.get_text().lower()
            if 'fazzolari' in full:
                idx = full.index('fazzolari')
                print(f'Query {q}: Found in text at pos {idx}: ...{full[max(0,idx-100):idx+200]}...')
            else:
                print(f'Query {q}: No fazzolari found in page text')
except Exception as e:
    print(f'Error: {e}')

# 4. Yelp search
print('\n=== Yelp Search ===')
try:
    url4 = 'https://www.yelp.com/search?find_desc=fazzolari&find_loc=Vancouver%2C+WA+98662'
    r4 = requests.get(url4, headers=headers, timeout=15)
    soup4 = BeautifulSoup(r4.text, 'html.parser')
    full4 = soup4.get_text().lower()
    if 'fazzolari' in full4:
        idx = full4.index('fazzolari')
        print(f'Found on Yelp: ...{full4[max(0,idx-100):idx+300]}...')
    else:
        print('No fazzolari found on Yelp')
except Exception as e:
    print(f'Error: {e}')

print('\nDone.')
