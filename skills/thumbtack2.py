import urllib.request
import json
import re

url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print(f'Redirecting to: {newurl}')
        new_req = urllib.request.Request(newurl)
        for k, v in req.headers.items():
            new_req.add_header(k, v)
        return new_req

opener = urllib.request.build_opener(RedirectHandler)
req = urllib.request.Request(url, headers=headers)

try:
    resp = opener.open(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    print(f'Status: {resp.status}')
    print(f'Final URL: {resp.url}')
    print(f'HTML length: {len(html)}')
    
    # Try JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'Found {len(ld_blocks)} JSON-LD blocks')
    for i, block in enumerate(ld_blocks):
        try:
            data = json.loads(block)
            print(f'\nJSON-LD block {i}: {json.dumps(data, indent=2)[:2000]}')
        except:
            print(f'Block {i} not valid JSON')
    
    # Try to find contractor names in HTML
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
    reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    print(f'\nFound {len(names)} names, {len(ratings)} ratings, {len(reviews)} review counts')
    for n in names[:20]:
        print(f'  Name: {n}')
    
    # Also look for data in __NEXT_DATA__ or similar
    next_data = re.findall(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_data:
        print(f'\nFound __NEXT_DATA__, length: {len(next_data[0])}')
        try:
            nd = json.loads(next_data[0])
            # Look for pros/contractors in the data
            nd_str = json.dumps(nd)
            # Find all ratingValue occurrences
            rating_contexts = [(m.start(), nd_str[max(0,m.start()-200):m.end()+100]) for m in re.finditer(r'ratingValue', nd_str)]
            for pos, ctx in rating_contexts[:5]:
                print(f'Rating context at {pos}: ...{ctx}...')
        except:
            print('Could not parse __NEXT_DATA__')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
