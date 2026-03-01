import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try Angi page
try:
    req = urllib.request.Request(
        'https://www.angi.com/companylist/us/wa/vancouver/fazzolari-custom-homes-and-renovations-reviews-5529634.htm',
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for rating patterns
    rating_matches = re.findall(r'(\d\.\d)\s*(?:out of|/|stars)', html, re.I)
    review_matches = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', html, re.I)
    print('=== ANGI ===')
    print(f'Ratings found: {rating_matches[:5]}')
    print(f'Reviews found: {review_matches[:5]}')
    # Also look for structured data
    ld_json = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
    review_count = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    print(f'LD+JSON rating: {ld_json}')
    print(f'LD+JSON reviewCount: {review_count}')
except Exception as e:
    print(f'Angi error: {e}')

# Try BBB page
try:
    req = urllib.request.Request(
        'https://www.bbb.org/us/wa/vancouver/profile/home-builders/fazzolari-custom-homes-inc-1296-22007670',
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode('utf-8', errors='ignore')
    rating_matches = re.findall(r'(\d\.\d)\s*(?:out of|/|stars)', html, re.I)
    review_matches = re.findall(r'(\d+)\s*(?:reviews?|ratings?|complaints?)', html, re.I)
    bbb_rating = re.findall(r'BBB Rating:\s*([A-F][+-]?)', html, re.I)
    print('\n=== BBB ===')
    print(f'BBB Rating: {bbb_rating}')
    print(f'Ratings found: {rating_matches[:5]}')
    print(f'Reviews found: {review_matches[:5]}')
except Exception as e:
    print(f'BBB error: {e}')

# Try Google search for explicit rating
try:
    query = 'site:google.com/maps Fazzolari+Construction+Vancouver+WA'
    url = f'https://html.duckduckgo.com/html/?q={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode('utf-8', errors='ignore')
    snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.S)
    print('\n=== Google Maps Search ===')
    for s in snippets[:3]:
        clean = re.sub(r'<[^>]+>', '', s).strip()
        print(clean[:200])
except Exception as e:
    print(f'Google Maps search error: {e}')

# Try Houzz
try:
    query = 'Fazzolari+Construction+Vancouver+WA+houzz+reviews'
    url = f'https://html.duckduckgo.com/html/?q={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode('utf-8', errors='ignore')
    snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.S)
    print('\n=== Houzz Search ===')
    for s in snippets[:5]:
        clean = re.sub(r'<[^>]+>', '', s).strip()
        print(clean[:200])
except Exception as e:
    print(f'Houzz search error: {e}')
