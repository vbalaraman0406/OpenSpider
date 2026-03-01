import urllib.request
import urllib.parse
import re

def fetch_page(url, label):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        # Clean HTML to text
        html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', html_clean)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        return f'Error fetching {label}: {e}'

# 1. Fetch Yelp page for Reliable Men Construction
print('=== YELP SEARCH ===')
yelp_url = 'https://www.yelp.com/biz/reliable-men-construction-vancouver'
text = fetch_page(yelp_url, 'Yelp')
# Look for rating and review info
keywords = ['rating', 'review', 'star', 'reliable men', 'bathroom', 'remodel', 'service', 'phone']
sentences = text.split('.')
for s in sentences:
    lower = s.lower()
    if any(k in lower for k in keywords):
        print(s.strip()[:200])
print()

# Also search for their direct website
print('=== SEARCHING FOR WEBSITE ===')
ddg_url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote('"Reliable Men Construction" Vancouver WA website')
text2 = fetch_page(ddg_url, 'DDG website search')
# Find URLs
urls_found = re.findall(r'https?://[^\s"<>]+reliable[^\s"<>]*', text2, re.IGNORECASE)
for u in urls_found[:10]:
    print(u)
