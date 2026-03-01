import urllib.request
import urllib.parse
import json
import re
from html.parser import HTMLParser

results = []

# Try Porch.com
try:
    url = 'https://porch.com/vancouver-wa/bathroom-remodelers'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for JSON-LD
    ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    for m in ld_matches:
        try:
            data = json.loads(m)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'GeneralContractor']:
                        results.append({'name': item.get('name',''), 'rating': item.get('aggregateRating',{}).get('ratingValue','N/A'), 'reviews': item.get('aggregateRating',{}).get('reviewCount','N/A'), 'phone': item.get('telephone','N/A'), 'url': item.get('url','N/A'), 'source': 'Porch'})
            elif isinstance(data, dict):
                if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'GeneralContractor']:
                    results.append({'name': data.get('name',''), 'rating': data.get('aggregateRating',{}).get('ratingValue','N/A'), 'reviews': data.get('aggregateRating',{}).get('reviewCount','N/A'), 'phone': data.get('telephone','N/A'), 'url': data.get('url','N/A'), 'source': 'Porch'})
        except: pass
    # Also try regex for contractor cards
    names = re.findall(r'data-testid="pro-name"[^>]*>([^<]+)', html)
    ratings = re.findall(r'data-testid="pro-rating"[^>]*>([^<]+)', html)
    print(f'Porch: found {len(names)} names, {len(ratings)} ratings')
    if not results and names:
        for i, name in enumerate(names[:20]):
            r = ratings[i] if i < len(ratings) else 'N/A'
            results.append({'name': name.strip(), 'rating': r, 'reviews': 'N/A', 'phone': 'N/A', 'url': 'N/A', 'source': 'Porch'})
    # Save raw for debug
    with open('porch_raw.html', 'w') as f:
        f.write(html[:50000])
    print(f'Porch total results: {len(results)}')
except Exception as e:
    print(f'Porch error: {e}')

# Try Thumbtack with redirect following
try:
    url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml', 'Accept-Language': 'en-US,en;q=0.9'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    tt_count = 0
    for m in ld_matches:
        try:
            data = json.loads(m)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'ProfessionalService']:
                    ar = item.get('aggregateRating', {})
                    results.append({'name': item.get('name',''), 'rating': ar.get('ratingValue','N/A'), 'reviews': ar.get('reviewCount','N/A'), 'phone': item.get('telephone','N/A'), 'url': item.get('url','N/A'), 'source': 'Thumbtack'})
                    tt_count += 1
        except: pass
    print(f'Thumbtack JSON-LD: {tt_count}')
    if tt_count == 0:
        with open('thumbtack_raw.html', 'w') as f:
            f.write(html[:50000])
        print(f'Thumbtack HTML length: {len(html)}')
except Exception as e:
    print(f'Thumbtack error: {e}')

# Try Networx
try:
    url = 'https://www.networx.com/bathroom-remodeling/vancouver-wa'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    nx_count = 0
    for m in ld_matches:
        try:
            data = json.loads(m)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if 'name' in item and item.get('@type') not in ['WebPage', 'WebSite', 'BreadcrumbList']:
                    ar = item.get('aggregateRating', {})
                    results.append({'name': item.get('name',''), 'rating': ar.get('ratingValue','N/A'), 'reviews': ar.get('reviewCount','N/A'), 'phone': item.get('telephone','N/A'), 'url': item.get('url','N/A'), 'source': 'Networx'})
                    nx_count += 1
        except: pass
    print(f'Networx JSON-LD: {nx_count}')
except Exception as e:
    print(f'Networx error: {e}')

# Print all results
print(f'\n=== TOTAL: {len(results)} ===')
for r in results:
    print(f"{r['name']} | {r['rating']} | {r['reviews']} | {r['phone']} | {r['url']} | {r['source']}")
