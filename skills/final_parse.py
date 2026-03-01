import urllib.request
import json
import re

# 1. Parse Reliable Men from BuildZoom JSON-LD
url = 'https://www.buildzoom.com/contractor/reliable-men-construction-llc'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract JSON-LD
    jsonld = re.findall(r'\{"@context":"https://schema\.org"[^<]+', html)
    if jsonld:
        data = json.loads(jsonld[0])
        print('=== Reliable Men - BuildZoom JSON-LD ===')
        print(f"Name: {data.get('name')}")
        print(f"Phone: {data.get('telephone')}")
        addr = data.get('address', {})
        print(f"Address: {addr.get('streetAddress')}, {addr.get('addressLocality')}, {addr.get('addressRegion')} {addr.get('postalCode')}")
        agg = data.get('aggregateRating', {})
        print(f"Rating: {agg.get('ratingValue')} / {agg.get('bestRating')}")
        print(f"Review Count: {agg.get('reviewCount')}")
        print(f"URL: {data.get('url')}")
except Exception as e:
    print(f'BuildZoom error: {e}')

# 2. Try Let's Remodel lander page
print('\n=== Lets Remodel - Lander ===')
try:
    req2 = urllib.request.Request('https://www.letsremodel.com/lander', headers={'User-Agent': 'Mozilla/5.0'})
    resp2 = urllib.request.urlopen(req2, timeout=15)
    html2 = resp2.read().decode('utf-8', errors='ignore')
    title = re.search(r'<title>(.*?)</title>', html2, re.I)
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html2)
    print(f"Title: {title.group(1) if title else 'N/A'}")
    print(f"Phones: {phones[:5]}")
    # Look for location
    loc = re.findall(r'Vancouver|Portland|WA|Oregon', html2, re.I)
    print(f"Location mentions: {list(set(loc))[:5]}")
    # Preview
    clean = re.sub(r'<[^>]+>', ' ', html2)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(f"Preview: {clean[:500]}")
except Exception as e:
    print(f'Lets Remodel error: {e}')

# 3. Try Mountainwood deeper
print('\n=== Mountainwood - Site ===')
try:
    req3 = urllib.request.Request('https://www.mountainwoodhomes.com', headers={'User-Agent': 'Mozilla/5.0'})
    resp3 = urllib.request.urlopen(req3, timeout=15)
    html3 = resp3.read().decode('utf-8', errors='ignore')
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html3)
    print(f"Phones: {phones[:5]}")
    # services
    services = re.findall(r'(?:bathroom|tile|vanity|remodel|kitchen|floor)[^<]{0,80}', html3, re.I)
    print(f"Service mentions: {services[:5]}")
except Exception as e:
    print(f'Mountainwood error: {e}')
