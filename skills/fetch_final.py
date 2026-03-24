import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Get full article on top 3 cyber attacks
url = 'https://cybersecuritynews.com/top-3-cyber-attacks-in-march-2026/'
try:
    resp = requests.get(url, headers=headers, timeout=10)
    text = resp.text
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # Get headings
    headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', text, flags=re.DOTALL)
    for h in headings:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        if len(clean) > 5:
            print(f'HEADING: {clean}')
    print()
    # Get all paragraphs with more content
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text, flags=re.DOTALL)
    for p in paragraphs[3:30]:
        t = re.sub(r'<[^>]+>', '', p).strip()
        if len(t) > 20:
            print(t[:500])
            print()
except Exception as e:
    print(f'ERROR: {e}')

# Search for recent financial sector breaches
print('\n=== RECENT FINANCIAL BREACHES ===')
try:
    url2 = 'https://html.duckduckgo.com/html/?q=financial+institution+data+breach+2026+march'
    resp2 = requests.get(url2, headers=headers, timeout=10)
    links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>', resp2.text)
    snippets = re.findall(r'<a class="result__snippet"[^>]*>(.+?)</a>', resp2.text)
    for i, (link, title) in enumerate(links[:5]):
        ct = re.sub(r'<[^>]+>', '', title)
        sn = re.sub(r'<[^>]+>', '', snippets[i]) if i < len(snippets) else ''
        print(f'TITLE: {ct}')
        print(f'SNIPPET: {sn[:250]}')
        print('---')
except Exception as e:
    print(f'ERROR: {e}')
