import urllib.request
import json
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

contractors = []

# Try Houzz with correct URL patterns
houzz_urls = [
    'https://www.houzz.com/professionals/bathroom-remodeling-and-addition/vancouver--wa-probr0-bo~t_11830~r_4956764',
    'https://www.houzz.com/professionals/general-contractors/vancouver--wa-probr0-bo~t_11786~r_4956764',
    'https://www.houzz.com/professionals/tile-stone-and-countertops/vancouver--wa-probr0-bo~t_11828~r_4956764',
]

for url in houzz_urls:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract JSON-LD
        ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        for block in ld_blocks:
            try:
                data = json.loads(block)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'GeneralContractor']:
                            contractors.append({
                                'name': item.get('name', 'N/A'),
                                'rating': item.get('aggregateRating', {}).get('ratingValue', 'N/A'),
                                'reviews': item.get('aggregateRating', {}).get('reviewCount', 'N/A'),
                                'phone': item.get('telephone', 'N/A'),
                                'url': item.get('url', 'N/A'),
                                'source': 'Houzz'
                            })
                elif isinstance(data, dict):
                    if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'GeneralContractor']:
                        contractors.append({
                            'name': data.get('name', 'N/A'),
                            'rating': data.get('aggregateRating', {}).get('ratingValue', 'N/A'),
                            'reviews': data.get('aggregateRating', {}).get('reviewCount', 'N/A'),
                            'phone': data.get('telephone', 'N/A'),
                            'url': data.get('url', 'N/A'),
                            'source': 'Houzz'
                        })
            except: pass
        # Also try regex for business names and ratings in HTML
        if len(contractors) == 0:
            names = re.findall(r'"proName":"([^"]+)"', html)
            ratings = re.findall(r'"averageRating":([\d.]+)', html)
            reviews_ct = re.findall(r'"numReviews":(\d+)', html)
            for i, name in enumerate(names[:15]):
                contractors.append({
                    'name': name,
                    'rating': ratings[i] if i < len(ratings) else 'N/A',
                    'reviews': reviews_ct[i] if i < len(reviews_ct) else 'N/A',
                    'phone': 'N/A',
                    'url': 'See Houzz',
                    'source': 'Houzz'
                })
        print(f'Houzz {url}: found {len(contractors)} total so far')
    except Exception as e:
        print(f'Houzz error: {e}')

# Try Thumbtack with redirect following
try:
    tt_url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(tt_url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html',
    })
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for block in ld_blocks:
        try:
            data = json.loads(block)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'ProfessionalService']:
                    contractors.append({
                        'name': item.get('name', 'N/A'),
                        'rating': item.get('aggregateRating', {}).get('ratingValue', 'N/A') if item.get('aggregateRating') else 'N/A',
                        'reviews': item.get('aggregateRating', {}).get('reviewCount', 'N/A') if item.get('aggregateRating') else 'N/A',
                        'phone': item.get('telephone', 'N/A'),
                        'url': item.get('url', 'N/A'),
                        'source': 'Thumbtack'
                    })
        except: pass
    print(f'Thumbtack: found {len(contractors)} total')
except Exception as e:
    print(f'Thumbtack error: {e}')

# Try BuildZoom
try:
    bz_url = 'https://www.buildzoom.com/wa/vancouver/bathroom-remodeling'
    req = urllib.request.Request(bz_url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html',
    })
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    names = re.findall(r'"name":\s*"([^"]{5,60})"', html)
    ratings = re.findall(r'"ratingValue":\s*"?([\d.]+)', html)
    for i, name in enumerate(names[:10]):
        if any(kw in name.lower() for kw in ['construction', 'remodel', 'tile', 'bath', 'home', 'build', 'renovation', 'plumb', 'design', 'kitchen', 'floor', 'llc', 'inc', 'co']):
            contractors.append({
                'name': name,
                'rating': ratings[i] if i < len(ratings) else 'N/A',
                'reviews': 'N/A',
                'phone': 'N/A',
                'url': 'See BuildZoom',
                'source': 'BuildZoom'
            })
    print(f'BuildZoom: found {len(contractors)} total')
except Exception as e:
    print(f'BuildZoom error: {e}')

print(f'\n=== TOTAL CONTRACTORS: {len(contractors)} ===')
for c in contractors:
    print(f"{c['name']} | {c['rating']} | {c['reviews']} | {c['phone']} | {c['url']} | {c['source']}")
