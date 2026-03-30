import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

try:
    resp = session.get('https://fantasy.formula1.com', timeout=15, allow_redirects=True)
    print(f'Fantasy F1 status: {resp.status_code}')
    print(f'URL: {resp.url}')
    text = re.sub(r'<[^>]+>', ' ', resp.text)
    text = re.sub(r'\s+', ' ', text)
    print(text[:500])
except Exception as e:
    print(f'Error: {e}')
