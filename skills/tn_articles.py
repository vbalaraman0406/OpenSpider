import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def extract_text(html, max_len=2500):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len]

urls = [
    'https://en.wikipedia.org/wiki/2026_Tamil_Nadu_Legislative_Assembly_election',
    'https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Tamil_Nadu_Legislative_Assembly_election',
]

for url in urls:
    print(f'\n{"="*60}')
    print(f'URL: {url}')
    print('='*60)
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            text = extract_text(r.text)
            print(text)
        else:
            print(f'Status: {r.status_code}')
    except Exception as e:
        print(f'Error: {e}')
