import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

results = {}

# 1. Google search for 'Fazzolari Construction Vancouver Washington'
try:
    url = 'https://www.google.com/search?q=Fazzolari+Construction+Vancouver+Washington'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Extract all links and their text
    links_data = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)[:200]
        if 'fazzolari' in href.lower() or 'fazzolari' in text.lower():
            links_data.append({'href': href[:300], 'text': text})
    
    # Also look for business info panel (Knowledge Panel)
    panel_text = ''
    for div in soup.find_all(['div', 'span']):
        t = div.get_text(strip=True).lower()
        if 'fazzolari' in t and len(div.get_text(strip=True)) > 20:
            panel_text += div.get_text(strip=True)[:500] + '\n---\n'
            if len(panel_text) > 2000:
                break
    
    results['google_links'] = links_data[:10]
    results['google_panel'] = panel_text[:2000]
except Exception as e:
    results['google_error'] = str(e)

# 2. Try searching Google for 'Fazzolari Construction LLC Vancouver WA'
try:
    url2 = 'https://www.google.com/search?q=%22Fazzolari%22+contractor+%22Vancouver+WA%22'
    r2 = requests.get(url2, headers=headers, timeout=15)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    links2 = []
    for a in soup2.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)[:200]
        if 'fazzolari' in href.lower() or 'fazzolari' in text.lower():
            links2.append({'href': href[:300], 'text': text})
    
    results['google2_links'] = links2[:10]
except Exception as e:
    results['google2_error'] = str(e)

# 3. Try to find on Houzz
try:
    url3 = 'https://www.houzz.com/professionals/general-contractor/fazzolari-pfvwus-pf~1234567890'
    # Actually search houzz
    url3 = 'https://www.google.com/search?q=site:houzz.com+Fazzolari+Vancouver+WA'
    r3 = requests.get(url3, headers=headers, timeout=15)
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    links3 = []
    for a in soup3.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)[:200]
        if 'houzz' in href.lower() and 'fazzolari' in text.lower():
            links3.append({'href': href[:300], 'text': text})
    results['houzz_links'] = links3[:5]
except Exception as e:
    results['houzz_error'] = str(e)

# 4. Try WA Secretary of State business search
try:
    url4 = 'https://www.google.com/search?q=%22Fazzolari%22+site:sos.wa.gov'
    r4 = requests.get(url4, headers=headers, timeout=15)
    soup4 = BeautifulSoup(r4.text, 'html.parser')
    links4 = []
    for a in soup4.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)[:200]
        if 'fazzolari' in text.lower() or 'sos.wa.gov' in href.lower():
            links4.append({'href': href[:300], 'text': text})
    results['sos_links'] = links4[:5]
except Exception as e:
    results['sos_error'] = str(e)

print(json.dumps(results, indent=2))
