import urllib.request
import re
import html

def fetch_and_extract(url, label, max_sentences=25):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
        text = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'[.!]\s', text)
        cost_sentences = []
        keywords = ['cost', 'price', 'per square', 'sq ft', 'average', 'range', 'labor',
                     'ceramic', 'porcelain', 'stone', 'marble', 'vanity', 'install',
                     'material', '$', 'budget', 'total', 'tile', 'counter', 'sink',
                     'prefab', 'custom', 'stock', 'removal', 'paid', 'spend', 'fee']
        for s in sentences:
            s = s.strip()
            if 30 < len(s) < 500:
                if any(k in s.lower() for k in keywords):
                    cost_sentences.append(s)
        print(f'\n=== {label} ===')
        print(f'URL: {url}')
        for cs in cost_sentences[:max_sentences]:
            print(f'  - {cs}')
        if not cost_sentences:
            print('  [No relevant cost data extracted]')
    except Exception as e:
        print(f'\n=== {label} === ERROR: {e}')

# Try alternative vanity cost sources
fetch_and_extract('https://www.forbes.com/home-improvement/bathroom/vanity-installation-cost/', 'Forbes - Vanity Installation Cost')
fetch_and_extract('https://www.bobvila.com/articles/cost-to-install-bathroom-vanity/', 'Bob Vila - Vanity Install Cost')
fetch_and_extract('https://www.angi.com/articles/how-much-does-bathroom-vanity-cost.htm', 'Angi - Vanity Cost')

# Also try for tile cost from Forbes
fetch_and_extract('https://www.forbes.com/home-improvement/flooring/tile-flooring-installation-cost/', 'Forbes - Tile Flooring Cost')
fetch_and_extract('https://www.forbes.com/home-improvement/bathroom/bathroom-tile-cost/', 'Forbes - Bathroom Tile Cost')
