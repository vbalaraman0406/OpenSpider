import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

queries = [
    'best+rated+bathroom+remodel+contractors+Vancouver+WA+98662',
    'bathroom+tile+vanity+contractor+Vancouver+Washington+reviews',
    'bathroom+renovation+contractor+Vancouver+WA+top+rated'
]

all_text = ''
for q in queries:
    url = f'https://www.bing.com/search?q={q}&count=20'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract visible text between tags
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        all_text += clean + '\n---QUERY_BREAK---\n'
        print(f'Query: {q} => got {len(clean)} chars')
    except Exception as e:
        print(f'Error for {q}: {e}')

# Save raw text for analysis
with open('bing_raw.txt', 'w') as f:
    f.write(all_text[:50000])

# Try to find contractor-like patterns
patterns = [
    r'(\d\.\d)\s*(?:star|/5|out of)',
    r'(\d+)\s*reviews?',
    r'\(\d{3}\)\s*\d{3}-\d{4}',
    r'\d{3}-\d{3}-\d{4}'
]

for p in patterns:
    matches = re.findall(p, all_text[:20000])
    if matches:
        print(f'Pattern {p}: {matches[:10]}')

# Extract potential business names - look for capitalized phrases near ratings
biz_pattern = r'([A-Z][A-Za-z&\']+(?:\s+[A-Z][A-Za-z&\']+){1,5})\s*[·\-|]'
biz_matches = re.findall(biz_pattern, all_text[:20000])
print(f'\nPotential businesses: {biz_matches[:20]}')

print(f'\nTotal text length: {len(all_text)}')
print('\nFirst 3000 chars of cleaned text:')
print(all_text[:3000])
