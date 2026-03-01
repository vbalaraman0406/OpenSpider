import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    'Mountainwood+bathroom+remodel+Vancouver+WA',
    'Mountain+Wood+bathroom+remodel+Vancouver+WA+98662',
    'Mountainwood+contractor+Vancouver+WA',
    'Mountainwood+remodeling+Vancouver+Washington',
    'Mountain+Wood+Construction+Vancouver+WA',
    'Mountainwood+LLC+Vancouver+WA',
]

print('=== DUCKDUCKGO SEARCHES ===')
for q in queries:
    try:
        url = f'https://html.duckduckgo.com/html/?q={q}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.select('.result__a')
        if results:
            print(f'\nQuery: {q}')
            for res in results[:5]:
                title = res.get_text(strip=True)
                href = res.get('href', '')
                # Extract actual URL from DDG redirect
                if 'uddg=' in href:
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    href = parsed.get('uddg', [href])[0]
                print(f'  {title}')
                print(f'    URL: {href}')
    except Exception as e:
        print(f'Error for {q}: {e}')

# Try Yellow Pages
print('\n=== YELLOW PAGES ===')
try:
    yp_url = 'https://www.yellowpages.com/search?search_terms=Mountainwood&geo_location_terms=Vancouver%2C+WA'
    r = requests.get(yp_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    listings = soup.select('.info-section .business-name')
    if listings:
        for l in listings[:5]:
            print(f'  {l.get_text(strip=True)}')
    else:
        print('  No listings found')
        # Check if there are any results at all
        organic = soup.select('.search-results .result')
        print(f'  Total result divs: {len(organic)}')
except Exception as e:
    print(f'  Error: {e}')

# Try Facebook search
print('\n=== FACEBOOK SEARCH (via DDG) ===')
try:
    url = 'https://html.duckduckgo.com/html/?q=site%3Afacebook.com+Mountainwood+Vancouver+WA'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.select('.result__a')
    for res in results[:5]:
        title = res.get_text(strip=True)
        href = res.get('href', '')
        if 'uddg=' in href:
            import urllib.parse
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            href = parsed.get('uddg', [href])[0]
        if 'facebook' in href.lower():
            print(f'  {title}')
            print(f'    URL: {href}')
except Exception as e:
    print(f'  Error: {e}')

# Try Yelp search
print('\n=== YELP SEARCH (via DDG) ===')
try:
    url = 'https://html.duckduckgo.com/html/?q=site%3Ayelp.com+Mountainwood+Vancouver+WA'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.select('.result__a')
    for res in results[:5]:
        title = res.get_text(strip=True)
        href = res.get('href', '')
        if 'uddg=' in href:
            import urllib.parse
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            href = parsed.get('uddg', [href])[0]
        if 'yelp' in href.lower():
            print(f'  {title}')
            print(f'    URL: {href}')
except Exception as e:
    print(f'  Error: {e}')

print('\nDone.')
