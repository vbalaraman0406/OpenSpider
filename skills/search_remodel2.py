import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Check raw HTML of letsremodel.com
print('=== RAW HTML OF LETSREMODEL.COM ===')
try:
    r = requests.get('https://www.letsremodel.com', headers=headers, timeout=10)
    html = r.text
    # Check for meta tags, scripts, etc
    soup = BeautifulSoup(html, 'html.parser')
    
    # Meta tags
    for meta in soup.find_all('meta'):
        if meta.get('content') and len(meta.get('content', '')) > 10:
            print(f'Meta: {meta.get("name", meta.get("property", ""))}: {meta.get("content", "")[:200]}')
    
    # Check for phone in raw HTML
    phones = re.findall(r'[\(]?\d{3}[\)]?[\s.-]?\d{3}[\s.-]?\d{4}', html)
    if phones:
        print(f'Phones in HTML: {list(set(phones))}')
    
    # Check for any JSON-LD structured data
    for script in soup.find_all('script', type='application/ld+json'):
        print(f'JSON-LD: {script.string[:500] if script.string else "empty"}')
    
    # Print first 2000 chars of raw HTML to understand structure
    print(f'\nHTML preview (first 2000 chars):\n{html[:2000]}')
except Exception as e:
    print(f'Error: {e}')

# Try DuckDuckGo search
print('\n=== DUCKDUCKGO SEARCH ===')
try:
    ddg_url = 'https://html.duckduckgo.com/html/?q=Let%27s+Remodel+Vancouver+WA+contractor+bathroom'
    r = requests.get(ddg_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('a', class_='result__a')
    for res in results[:10]:
        print(f'{res.get_text(strip=True)}: {res.get("href", "")}')
except Exception as e:
    print(f'DDG error: {e}')

# Try Google Maps / Places search
print('\n=== GOOGLE SEARCH SPECIFIC ===')
try:
    gurl = 'https://www.google.com/search?q=%22Let%27s+Remodel%22+Vancouver+WA+contractor+phone+number'
    r = requests.get(gurl, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(separator='|', strip=True)
    # Find relevant segments
    segments = text.split('|')
    for seg in segments:
        seg_lower = seg.lower()
        if any(kw in seg_lower for kw in ['remodel', 'phone', 'rating', 'review', 'star', 'vancouver']):
            if len(seg) > 5 and len(seg) < 300:
                print(seg)
except Exception as e:
    print(f'Google error: {e}')
