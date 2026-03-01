import urllib.request
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

contractors = []

# Try Bing search
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

queries = [
    'bathroom+remodel+contractors+Vancouver+WA+98662+reviews',
    'bathroom+tile+vanity+replacement+Vancouver+Washington+rated',
]

for q in queries:
    url = f'https://www.bing.com/search?q={q}&count=20'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Bing query: {q[:50]}... => {len(html)} chars')
        
        # Extract result blocks - Bing uses <li class="b_algo">
        results = re.findall(r'<li class="b_algo">(.*?)</li>', html, re.DOTALL)
        print(f'  Found {len(results)} b_algo results')
        
        for r in results:
            # Extract title and URL
            title_match = re.search(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', r, re.DOTALL)
            snippet_match = re.search(r'<p[^>]*>(.*?)</p>', r, re.DOTALL)
            
            if title_match:
                link = title_match.group(1)
                title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
                snippet = ''
                if snippet_match:
                    snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                
                # Skip major listing sites
                skip = ['yelp.com', 'angi.com', 'homeadvisor.com', 'angieslist.com', 'bbb.org']
                if any(s in link.lower() for s in skip):
                    continue
                
                # Extract ratings from snippet
                rating = ''
                rating_match = re.search(r'(\d+\.\d+)\s*(?:star|/5|out of|rating)', snippet, re.I)
                if rating_match:
                    rating = rating_match.group(1)
                
                reviews = ''
                rev_match = re.search(r'(\d+)\s*(?:review|rating)', snippet, re.I)
                if rev_match:
                    reviews = rev_match.group(1)
                
                phone = ''
                phone_match = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', snippet)
                if phone_match:
                    phone = phone_match.group(0)
                
                print(f'  RESULT: {title[:60]} | {link[:60]} | rating={rating} | reviews={reviews}')
                print(f'    Snippet: {snippet[:150]}')
                
                contractors.append({
                    'name': title,
                    'url': link,
                    'rating': rating,
                    'reviews': reviews,
                    'phone': phone,
                    'snippet': snippet[:200]
                })
    except Exception as e:
        print(f'Bing error: {e}')

# Also try Thumbtack with proper redirect following
try:
    url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    print(f'\nThumbtack: {len(html)} chars, status={resp.status}')
    
    # Look for JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'  JSON-LD blocks: {len(ld_blocks)}')
    for block in ld_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'LocalBusiness':
                        name = item.get('name', '')
                        rating = ''
                        reviews = ''
                        if 'aggregateRating' in item:
                            rating = str(item['aggregateRating'].get('ratingValue', ''))
                            reviews = str(item['aggregateRating'].get('reviewCount', ''))
                        phone = item.get('telephone', '')
                        url = item.get('url', '')
                        print(f'  TT: {name} | {rating} | {reviews} reviews | {phone}')
                        contractors.append({
                            'name': name,
                            'url': url,
                            'rating': rating,
                            'reviews': reviews,
                            'phone': phone,
                            'snippet': 'Thumbtack - Bathroom Remodeling'
                        })
            elif isinstance(data, dict) and data.get('@type') == 'LocalBusiness':
                name = data.get('name', '')
                print(f'  TT single: {name}')
        except:
            pass
    
    # Also try regex for pro cards
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)', html)
    print(f'  Regex names: {len(names)}, ratings: {len(ratings)}')
    
except Exception as e:
    print(f'Thumbtack error: {e}')

print(f'\n=== TOTAL CONTRACTORS FOUND: {len(contractors)} ===')
for c in contractors:
    print(f"  {c['name'][:50]} | {c['rating']} | {c['reviews']} | {c['phone']} | {c['url'][:60]}")
