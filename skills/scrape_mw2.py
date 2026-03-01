import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Scrape bathroom remodel page
for page_url in ['https://www.mountainwoodhomes.com/bathroom-remodels/', 
                  'https://www.mountainwoodhomes.com/contact/',
                  'https://www.mountainwoodhomes.com/why-us/',
                  'https://www.mountainwoodhomes.com/awards-associations/']:
    print(f'\n=== {page_url} ===')
    try:
        resp = requests.get(page_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            # Remove duplicate blank lines
            lines = [l for l in text.split('\n') if l.strip()]
            clean = '\n'.join(lines)
            print(clean[:1500])
        else:
            print(f'Status: {resp.status_code}')
    except Exception as e:
        print(f'Error: {e}')
