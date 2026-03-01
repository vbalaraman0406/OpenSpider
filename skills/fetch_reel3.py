import urllib.request
import re
import html
import json

# Approach 1: Try Instagram oEmbed API
oembed_url = 'https://api.instagram.com/oembed/?url=https://www.instagram.com/reel/DVWEXdQEp-B/'
req = urllib.request.Request(oembed_url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    print('=== OEMBED API RESULT ===')
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f'oEmbed error: {e}')

print('\n' + '='*60 + '\n')

# Approach 2: Try fetching as Googlebot to get SSR content
url = 'https://www.instagram.com/reel/DVWEXdQEp-B/?igsh=MWloYWEzOG8zY2pvcQ=='
req2 = urllib.request.Request(url, headers={
    'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Accept': 'text/html',
})
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    page = resp2.read().decode('utf-8', errors='replace')
    print(f'=== GOOGLEBOT FETCH: {len(page)} chars ===')
    
    # Extract all meta tags
    meta_all = re.findall(r'<meta\s+([^>]+)>', page, re.IGNORECASE)
    print(f'Found {len(meta_all)} meta tags')
    for m in meta_all:
        prop = re.search(r'(?:property|name)=["\']([^"\']+)["\']', m)
        cont = re.search(r'content=["\']([^"\']*)["\']', m)
        if prop and cont:
            print(f'  {prop.group(1)}: {html.unescape(cont.group(1))[:300]}')
    
    title_match = re.search(r'<title>([^<]+)</title>', page)
    if title_match:
        print(f'\nTitle: {html.unescape(title_match.group(1))}')
    
    # Check for alternate link or canonical
    canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', page)
    if canonical:
        print(f'Canonical: {canonical.group(1)}')
    
    # Search for JSON-LD
    jsonld = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([^<]+)</script>', page)
    for j in jsonld:
        print(f'\nJSON-LD: {j[:1500]}')
        
except Exception as e:
    print(f'Googlebot fetch error: {e}')

print('\n' + '='*60 + '\n')

# Approach 3: Try fetching with curl-like headers (Facebook crawler)
req3 = urllib.request.Request(url, headers={
    'User-Agent': 'facebookexternalhit/1.1',
    'Accept': 'text/html',
})
try:
    resp3 = urllib.request.urlopen(req3, timeout=15)
    page3 = resp3.read().decode('utf-8', errors='replace')
    print(f'=== FACEBOOK CRAWLER FETCH: {len(page3)} chars ===')
    
    meta_all = re.findall(r'<meta\s+([^>]+)>', page3, re.IGNORECASE)
    for m in meta_all:
        prop = re.search(r'(?:property|name)=["\']([^"\']+)["\']', m)
        cont = re.search(r'content=["\']([^"\']*)["\']', m)
        if prop and cont:
            val = html.unescape(cont.group(1))
            if len(val) > 5:
                print(f'  {prop.group(1)}: {val[:300]}')
    
    title_match = re.search(r'<title>([^<]+)</title>', page3)
    if title_match:
        print(f'\nTitle: {html.unescape(title_match.group(1))}')
except Exception as e:
    print(f'Facebook crawler error: {e}')
