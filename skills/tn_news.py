import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch(name, url):
    print(f'\n=== {name} ===')
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        html = resp.text
        headlines = re.findall(r'<(?:h[1-4]|a)[^>]*>(.*?)</(?:h[1-4]|a)>', html, re.DOTALL)
        clean = []
        for h in headlines:
            t = re.sub(r'<[^>]+>', '', h).strip()
            t = re.sub(r'\s+', ' ', t)
            if len(t) > 25 and len(t) < 300:
                tl = t.lower()
                if any(kw in tl for kw in ['tamil', 'election', 'dmk', 'aiadmk', 'bjp', 'alliance', 'poll', 'seat', 'campaign', 'vote', 'stalin', 'annamalai', 'palaniswami', 'edappadi', 'ntk', 'seeman', 'kamal']):
                    if t not in clean:
                        clean.append(t)
        for c in clean[:12]:
            print(f'  - {c}')
        if not clean:
            print('  [No keyword-matched headlines]')
            all_links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            for href, text in all_links[:50]:
                t = re.sub(r'<[^>]+>', '', text).strip()
                if len(t) > 20 and ('tamil' in t.lower() or 'election' in t.lower()):
                    print(f'  LINK: {t}')
    except Exception as e:
        print(f'  Error: {e}')

import warnings
warnings.filterwarnings('ignore')

fetch('NDTV', 'https://www.ndtv.com/tamil-nadu-news')
fetch('India Today', 'https://www.indiatoday.in/india/tamil-nadu')
fetch('The Hindu', 'https://www.thehindu.com/news/national/tamil-nadu/')
fetch('Times of India', 'https://timesofindia.indiatimes.com/city/chennai')
fetch('News18', 'https://www.news18.com/tamil-nadu/')
fetch('Deccan Herald', 'https://www.deccanherald.com/india/tamil-nadu')

print('\n=== SEARCH FOR ELECTION SPECIFIC ===')
fetch('Google News TN Election', 'https://news.google.com/search?q=Tamil%20Nadu%20election%202026&hl=en-IN')

print('\nDONE')
