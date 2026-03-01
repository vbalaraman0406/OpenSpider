import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

results = {}

# 1. Try WA LNI contractor search
try:
    url = 'https://secure.lni.wa.gov/verify/Results.aspx'
    params = {
        'ContractorName': 'Fazzolari',
        'City': 'Vancouver',
        'SearchType': 'ContractorName'
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)[:2000]
    if 'fazzolari' in text.lower():
        results['WA_LNI'] = text
    else:
        results['WA_LNI'] = f'Status {r.status_code}, no fazzolari found in text'
except Exception as e:
    results['WA_LNI'] = str(e)

# 2. Try DuckDuckGo HTML search
try:
    url = 'https://html.duckduckgo.com/html/'
    data = {'q': 'Fazzolari contractor Vancouver WA bathroom remodel'}
    r = requests.post(url, data=data, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', class_='result__a')
    ddg_results = []
    for link in links[:10]:
        title = link.get_text(strip=True)
        href = link.get('href', '')
        ddg_results.append({'title': title, 'url': href})
    results['DDG'] = ddg_results if ddg_results else f'No results, status {r.status_code}'
except Exception as e:
    results['DDG'] = str(e)

# 3. Try Google search with different query
try:
    url = 'https://www.google.com/search'
    params = {'q': 'Fazzolari Construction Vancouver Washington'}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)
    if 'fazzolari' in text.lower():
        idx = text.lower().index('fazzolari')
        results['Google'] = text[max(0,idx-200):idx+500]
    else:
        # Get all links
        all_links = [a.get('href','') for a in soup.find_all('a') if 'fazzolari' in (a.get('href','') + a.get_text()).lower()]
        results['Google'] = f'Status {r.status_code}, fazzolari links: {all_links[:5]}'
except Exception as e:
    results['Google'] = str(e)

# 4. Try Yelp search
try:
    url = 'https://www.yelp.com/search'
    params = {'find_desc': 'Fazzolari', 'find_loc': 'Vancouver, WA 98662'}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)
    if 'fazzolari' in text.lower():
        idx = text.lower().index('fazzolari')
        results['Yelp'] = text[max(0,idx-100):idx+500]
    else:
        results['Yelp'] = f'Status {r.status_code}, no fazzolari found'
except Exception as e:
    results['Yelp'] = str(e)

# 5. Try searching for just the name on Google Maps
try:
    url = 'https://www.google.com/maps/search/Fazzolari+Vancouver+WA'
    r = requests.get(url, headers=headers, timeout=15)
    text = r.text
    if 'fazzolari' in text.lower():
        idx = text.lower().index('fazzolari')
        results['GoogleMaps'] = text[max(0,idx-100):idx+300]
    else:
        results['GoogleMaps'] = f'Status {r.status_code}, no fazzolari found'
except Exception as e:
    results['GoogleMaps'] = str(e)

print(json.dumps(results, indent=2, default=str))
