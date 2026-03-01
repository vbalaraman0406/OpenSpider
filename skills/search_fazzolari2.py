import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

queries = [
    'Fazzolari contractor Vancouver WA',
    'Fazzolari remodel Vancouver Washington',
    'Fazzolari construction Vancouver WA',
    'Fazzolari home improvement Vancouver WA 98662',
]

for query in queries:
    print(f'\n=== Searching: {query} ===')
    # Try Google
    url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num=10'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f'Google Status: {resp.status_code}')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Extract text snippets
        for div in soup.find_all(['div', 'span'], limit=50):
            text = div.get_text(strip=True)
            if 'fazzolari' in text.lower() and len(text) > 20 and len(text) < 500:
                print(f'  Found: {text[:200]}')
    except Exception as e:
        print(f'Google error: {e}')

    # Try Bing
    url2 = f'https://www.bing.com/search?q={requests.utils.quote(query)}'
    try:
        resp2 = requests.get(url2, headers=headers, timeout=15)
        print(f'Bing Status: {resp2.status_code}')
        soup2 = BeautifulSoup(resp2.text, 'html.parser')
        for li in soup2.find_all(['li', 'div', 'p'], limit=80):
            text = li.get_text(strip=True)
            if 'fazzolari' in text.lower() and len(text) > 20 and len(text) < 500:
                print(f'  Bing Found: {text[:200]}')
    except Exception as e:
        print(f'Bing error: {e}')
