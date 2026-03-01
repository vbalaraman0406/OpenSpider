import urllib.request
import urllib.parse
import json
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://www.buildzoom.com/contractor/wa/vancouver/bathroom-remodeling',
    'https://www.buildzoom.com/contractor/wa/vancouver/tile',
    'https://www.buildzoom.com/contractor/wa/vancouver/general-contractor',
]

contractors = []

for url in urls:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'URL: {url} - Status: {resp.status} - Length: {len(html)}')
        
        # Look for JSON-LD
        ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        for m in ld_matches:
            try:
                data = json.loads(m)
                print(f'JSON-LD: {json.dumps(data)[:500]}')
            except:
                pass
        
        # Try to find contractor names and ratings from HTML patterns
        # BuildZoom typically has contractor cards
        names = re.findall(r'class="[^"]*contractor[^"]*name[^"]*"[^>]*>([^<]+)<', html, re.I)
        if not names:
            names = re.findall(r'<h[23][^>]*>\s*<a[^>]*>([^<]+)</a>', html)
        print(f'Names found: {names[:10]}')
        
        # Extract rating patterns
        ratings = re.findall(r'(\d+\.\d+)\s*(?:stars?|rating|/\s*5)', html, re.I)
        print(f'Ratings found: {ratings[:10]}')
        
        # Extract phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        print(f'Phones found: {phones[:10]}')
        
        # Print a sample of the HTML to understand structure
        # Find contractor-related sections
        sections = re.findall(r'<div[^>]*class="[^"]*(?:contractor|result|listing|card)[^"]*"[^>]*>(.{200,500})', html, re.I | re.DOTALL)
        for s in sections[:3]:
            clean = re.sub(r'<[^>]+>', ' ', s)
            clean = re.sub(r'\s+', ' ', clean).strip()
            print(f'Section: {clean[:200]}')
        
        print('---')
    except Exception as e:
        print(f'Error for {url}: {e}')

print('\nDone.')
