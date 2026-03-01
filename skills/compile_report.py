import urllib.request
import re
import html
import json

def fetch_cost_data(url, label, max_sentences=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
        text = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'[.!]\s', text)
        keywords = ['cost', 'price', 'per square', 'sq ft', 'average', 'range', 'labor',
                     'ceramic', 'porcelain', 'stone', 'marble', 'vanity', 'install',
                     '$', 'total', 'tile', 'removal', 'budget', 'high-end', 'custom', 'prefab',
                     'per sq', 'nationally', 'homeowner']
        for s in sentences:
            s = s.strip()
            if 30 < len(s) < 350 and '$' in s:
                sl = s.lower()
                matches = sum(1 for k in keywords if k in sl)
                if matches >= 2:
                    results.append(s)
    except Exception as e:
        results.append(f'ERROR: {e}')
    return results

# Try multiple sources
sources = [
    ('https://www.forbes.com/home-improvement/bathroom/tile-installation-cost/', 'Forbes - Tile Installation Cost'),
    ('https://www.forbes.com/home-improvement/bathroom/bathroom-vanity-cost/', 'Forbes - Vanity Cost'),
    ('https://www.angi.com/articles/how-much-does-it-cost-install-tile.htm', 'Angi - Tile Install Cost'),
    ('https://www.angi.com/articles/how-much-does-it-cost-to-install-a-bathroom-vanity.htm', 'Angi - Vanity Install Cost'),
    ('https://www.homeadvisor.com/cost/flooring/install-tile/', 'HomeAdvisor - Tile Install'),
    ('https://www.homeadvisor.com/cost/bathrooms/bathroom-vanity-costs/', 'HomeAdvisor - Vanity Cost'),
]

all_data = {}
for url, label in sources:
    print(f'\nFetching: {label}...')
    results = fetch_cost_data(url, label)
    all_data[label] = results
    for r in results[:12]:
        print(f'  - {r}')
    if not results:
        print('  [No cost data with $ found]')

print('\n\n=== FETCH COMPLETE ===')
