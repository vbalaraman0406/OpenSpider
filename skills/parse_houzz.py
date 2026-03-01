import urllib.request
import json
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try multiple Houzz URLs for bathroom remodelers in Vancouver WA
urls = [
    'https://www.houzz.com/professionals/general-contractor/vancouver-wa-us',
    'https://www.houzz.com/professionals/design-build-firms/vancouver-wa-us',
]

all_contractors = []

for url in urls:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract JSON-LD
        pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        blocks = re.findall(pattern, html, re.DOTALL)
        
        for block in blocks:
            try:
                data = json.loads(block)
                if isinstance(data, dict) and data.get('@type') == 'LocalBusiness':
                    name = data.get('name', 'N/A')
                    rating = ''
                    reviews = ''
                    if 'aggregateRating' in data:
                        ar = data['aggregateRating']
                        rating = ar.get('ratingValue', '')
                        reviews = ar.get('reviewCount', '')
                    phone = data.get('telephone', '')
                    website = data.get('url', '')
                    addr = data.get('address', {})
                    location = ''
                    if addr:
                        location = f"{addr.get('addressLocality','')}, {addr.get('addressRegion','')}"
                    desc = data.get('description', '')[:100]
                    all_contractors.append({
                        'name': name,
                        'rating': rating,
                        'reviews': reviews,
                        'phone': phone,
                        'website': website,
                        'location': location,
                        'notes': desc
                    })
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'LocalBusiness':
                            name = item.get('name', 'N/A')
                            rating = ''
                            reviews = ''
                            if 'aggregateRating' in item:
                                ar = item['aggregateRating']
                                rating = ar.get('ratingValue', '')
                                reviews = ar.get('reviewCount', '')
                            phone = item.get('telephone', '')
                            website = item.get('url', '')
                            addr = item.get('address', {})
                            location = ''
                            if addr:
                                location = f"{addr.get('addressLocality','')}, {addr.get('addressRegion','')}"
                            desc = item.get('description', '')[:100]
                            all_contractors.append({
                                'name': name,
                                'rating': rating,
                                'reviews': reviews,
                                'phone': phone,
                                'website': website,
                                'location': location,
                                'notes': desc
                            })
            except json.JSONDecodeError:
                pass
        
        # Also try regex for pro cards in HTML
        pro_pattern = r'data-pro-title="([^"]+)"'
        pro_names = re.findall(pro_pattern, html)
        if pro_names:
            print(f"Found {len(pro_names)} pro cards in HTML")
            for pn in pro_names[:10]:
                print(f"  Pro: {pn}")
                
    except Exception as e:
        print(f"Error with {url}: {e}")

print(f"\nTotal contractors from JSON-LD: {len(all_contractors)}")
for c in all_contractors:
    print(f"Name: {c['name']}")
    print(f"  Rating: {c['rating']} ({c['reviews']} reviews)")
    print(f"  Phone: {c['phone']}")
    print(f"  Website: {c['website']}")
    print(f"  Location: {c['location']}")
    print(f"  Notes: {c['notes']}")
    print()

# Also try Thumbtack with correct URL
print("\n--- Trying Thumbtack ---")
try:
    tt_url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(tt_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    print(f"Thumbtack response: {len(html)} bytes")
    
    blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(blocks)} JSON-LD blocks")
    
    for block in blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                        name = item.get('name', 'N/A')
                        rating = ''
                        reviews = ''
                        if 'aggregateRating' in item:
                            ar = item['aggregateRating']
                            rating = ar.get('ratingValue', '')
                            reviews = ar.get('reviewCount', '')
                        phone = item.get('telephone', '')
                        website = item.get('url', '')
                        all_contractors.append({
                            'name': name, 'rating': rating, 'reviews': reviews,
                            'phone': phone, 'website': website, 'location': 'Vancouver, WA',
                            'notes': 'Thumbtack'
                        })
            elif isinstance(data, dict):
                t = data.get('@type', '')
                print(f"  Type: {t}, Name: {data.get('name','')}")
        except:
            pass
    
except Exception as e:
    print(f"Thumbtack error: {e}")

print(f"\nGrand total: {len(all_contractors)} contractors")
