import urllib.request
import urllib.parse
import re
import ssl
import time
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    return resp.read().decode('utf-8', errors='ignore')

# Save the raw HTML for inspection
q = 'best bathroom remodel contractors Vancouver WA 98662'
encoded = urllib.parse.quote_plus(q)
url = f'https://www.bing.com/search?q={encoded}'
html = fetch(url)

# Write HTML to file for inspection
with open('bing_raw.html', 'w') as f:
    f.write(html)

# Look for b_algo results (Bing organic)
algo_results = re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', html, re.DOTALL)
print(f'b_algo results: {len(algo_results)}')

# Look for any <a> with meaningful hrefs
all_links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
for href, text in all_links:
    text_clean = re.sub(r'<[^>]+>', '', text).strip()
    if text_clean and len(text_clean) > 5 and 'bing.com' not in href and 'microsoft.com' not in href:
        print(f'Link: {text_clean[:100]}')
        print(f'  URL: {href[:150]}')

# Look for structured data / JSON-LD
jsonld = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
if jsonld:
    print(f'\nJSON-LD blocks: {len(jsonld)}')
    for j in jsonld:
        try:
            data = json.loads(j)
            print(json.dumps(data, indent=2)[:500])
        except:
            print(j[:300])

# Look for any data attributes or patterns with business names
biz_patterns = re.findall(r'data-partnertag="([^"]+)"', html)
if biz_patterns:
    print(f'\nPartner tags: {biz_patterns}')

# Look for phone-like patterns with context
phone_contexts = re.findall(r'.{0,80}(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}).{0,80}', html)
for ctx_match in phone_contexts[:10]:
    if isinstance(ctx_match, tuple):
        print(f'Phone context: {ctx_match}')
    else:
        print(f'Phone: {ctx_match}')

# Look for rating patterns
ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', html, re.IGNORECASE)
if ratings:
    print(f'Ratings found: {ratings}')

# Check for specific class patterns
for pattern_name, pattern in [
    ('b_caption', r'<div class="b_caption"[^>]*>(.*?)</div>'),
    ('b_title', r'<div class="b_title"[^>]*>(.*?)</div>'),
    ('b_snippet', r'<p class="b_lineclamp[^"]*"[^>]*>(.*?)</p>'),
    ('b_factrow', r'<div class="b_factrow"[^>]*>(.*?)</div>'),
]:
    matches = re.findall(pattern, html, re.DOTALL)
    if matches:
        print(f'\n{pattern_name} ({len(matches)}):')
        for m in matches[:5]:
            clean = re.sub(r'<[^>]+>', ' ', m).strip()
            clean = re.sub(r'\s+', ' ', clean)
            if clean:
                print(f'  {clean[:200]}')

print('\n=== Trying Google with different approach ===')
# Try Google
q2 = 'bathroom+remodel+contractors+Vancouver+WA+98662+reviews'
url2 = f'https://www.google.com/search?q={q2}&num=20'
try:
    html2 = fetch(url2)
    print(f'Google HTML length: {len(html2)}')
    
    # Check for CAPTCHA
    if 'captcha' in html2.lower() or 'unusual traffic' in html2.lower():
        print('Google returned CAPTCHA')
    
    # Save for debugging
    with open('google_raw.html', 'w') as f:
        f.write(html2)
    
    # Extract visible text chunks that mention contractors
    text_only = re.sub(r'<[^>]+>', '\n', html2)
    text_only = re.sub(r'\n+', '\n', text_only)
    lines = [l.strip() for l in text_only.split('\n') if l.strip() and len(l.strip()) > 20]
    for line in lines:
        if any(kw in line.lower() for kw in ['bath', 'remodel', 'contractor', 'tile', 'renovation', 'plumb', 'vancouver']):
            print(f'  G: {line[:200]}')
except Exception as e:
    print(f'Google error: {e}')
