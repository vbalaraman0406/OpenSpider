import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try DuckDuckGo HTML
try:
    ddg_url = 'https://html.duckduckgo.com/html/?q=Reliable+Men+contractor+Vancouver+WA+bathroom+remodel'
    r = requests.get(ddg_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print('=== DUCKDUCKGO RESULTS ===')
    for result in soup.find_all('div', class_='result'):
        title = result.find('a', class_='result__a')
        snippet = result.find('a', class_='result__snippet')
        if title:
            print(f'Title: {title.get_text(strip=True)}')
            href = title.get('href', '')
            print(f'URL: {href}')
        if snippet:
            print(f'Snippet: {snippet.get_text(strip=True)}')
        print('---')
except Exception as e:
    print(f'DDG error: {e}')

# Try common URL patterns directly
print('\n=== DIRECT URL ATTEMPTS ===')
urls_to_try = [
    'https://www.reliablemen.com',
    'https://reliablemen.com',
    'https://www.reliablemenllc.com',
    'https://reliablemenllc.com',
    'https://www.reliablemencontracting.com',
    'https://www.reliablemenservices.com',
    'https://www.reliablemenhomeservices.com',
]

for url in urls_to_try:
    try:
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            print(f'\nFOUND: {url} -> {r.url} (status {r.status_code})')
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            print(f'Page Title: {title.get_text(strip=True) if title else "N/A"}')
            # Get meta description
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta:
                print(f'Description: {meta.get("content", "")}')
            # Look for phone numbers
            text = soup.get_text()
            import re
            phones = re.findall(r'[\(]?\d{3}[\)]?[\s.-]?\d{3}[\s.-]?\d{4}', text)
            if phones:
                print(f'Phone numbers found: {list(set(phones))}')
            # Print first 500 chars of body text
            body_text = ' '.join(text.split())[:500]
            print(f'Body preview: {body_text}')
        else:
            print(f'{url} -> status {r.status_code}')
    except Exception as e:
        print(f'{url} -> Error: {type(e).__name__}')
