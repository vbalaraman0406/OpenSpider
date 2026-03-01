import urllib.request
import re
import json

# Try Thumbtack directly for Vancouver WA bathroom remodeling
urls = [
    ('Thumbtack', 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'),
    ('Houzz', 'https://www.houzz.com/professionals/general-contractors/bathroom-remodeling/vancouver--wa'),
    ('HomeAdvisor', 'https://www.homeadvisor.com/c.Bathroom-Remodel.Vancouver.WA.-12014.html'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

for name, url in urls:
    print(f'\n=== {name} ===')
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Status: {resp.status}, Length: {len(html)}')
        
        # Look for JSON-LD data
        jsonld = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if jsonld:
            for j in jsonld[:3]:
                try:
                    data = json.loads(j)
                    print(f'JSON-LD type: {data.get("@type", "unknown")}')
                    if isinstance(data, list):
                        for item in data[:5]:
                            print(f"  Name: {item.get('name','?')}, Rating: {item.get('aggregateRating',{}).get('ratingValue','?')}")
                    elif data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                        print(f"  Name: {data.get('name','?')}, Rating: {data.get('aggregateRating',{}).get('ratingValue','?')}")
                except:
                    print(f'  JSON parse error, first 200: {j[:200]}')
        
        # Try to find contractor names and ratings in HTML
        # Thumbtack pattern
        names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
        ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
        
        if names:
            print(f'Found {len(names)} names, {len(ratings)} ratings, {len(reviews)} review counts')
            for i, n in enumerate(names[:15]):
                r = ratings[i] if i < len(ratings) else '?'
                rc = reviews[i] if i < len(reviews) else '?'
                print(f'  {n} | Rating: {r} | Reviews: {rc}')
        else:
            # Try generic patterns
            biz = re.findall(r'class="[^"]*pro-name[^"]*"[^>]*>([^<]+)', html)
            if not biz:
                biz = re.findall(r'class="[^"]*business-name[^"]*"[^>]*>([^<]+)', html)
            if biz:
                print(f'Found {len(biz)} businesses: {biz[:10]}')
            else:
                print(f'No contractor names found. Sample (1000-2000): {html[1000:2000]}')
    except Exception as e:
        print(f'Error: {e}')
