import urllib.request
import re
import html

def fetch_and_extract(url, label, max_sentences=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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
                     'prefab', 'custom', 'stock', 'removal']
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
            print('  [No relevant data found]')
    except Exception as e:
        print(f'\n=== {label} === ERROR: {e}')

# Vanity costs
fetch_and_extract('https://www.homeadvisor.com/cost/bathrooms/install-a-bathroom-vanity/', 'HomeAdvisor - Vanity Install Cost')
fetch_and_extract('https://www.fixr.com/costs/bathroom-vanity-installation', 'Fixr - Vanity Installation Cost')

# Wall tile specifics
fetch_and_extract('https://archieremodels.com/bathroom-wall-tile-cost-materials-labor-total-price/', 'Archie Remodels - Wall Tile Cost')
