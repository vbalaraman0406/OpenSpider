import urllib.request
import urllib.parse
import re
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    return resp.read().decode('utf-8', errors='ignore')

# --- Approach 1: DuckDuckGo HTML search ---
print("=== DuckDuckGo Search ===")
try:
    query = 'bathroom tile remodeling contractor Orchards Vancouver WA reviews'
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}'
    html = fetch(url)
    # DuckDuckGo results are in <a class="result__a" ...>
    results = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    if not results:
        results = re.findall(r'<a[^>]+href="([^"]+)"[^>]*class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    for i, (href, title_html) in enumerate(results[:10]):
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        print(f"  {i+1}. {title[:120]}")
        print(f"     {href[:150]}")
    if not results:
        # Try broader pattern
        links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        for i, (href, t) in enumerate(links[:15]):
            title = re.sub(r'<[^>]+>', '', t).strip()
            if len(title) > 5 and 'duckduckgo' not in href:
                print(f"  Link: {title[:100]} -> {href[:120]}")
        print(f"  HTML snippet: {html[1000:2000]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(3)

# --- Approach 2: Try Thumbtack directly ---
print("\n=== Thumbtack Direct ===")
try:
    url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    html = fetch(url)
    # Extract contractor names and ratings
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)', html)
    review_counts = re.findall(r'"reviewCount"\s*:\s*"?(\d+)', html)
    print(f"  Found {len(names)} names, {len(ratings)} ratings")
    for i, name in enumerate(names[:10]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        rc = review_counts[i] if i < len(review_counts) else 'N/A'
        print(f"  {i+1}. {name} | Rating: {r} | Reviews: {rc}")
    if not names:
        print(f"  HTML length: {len(html)}")
        print(f"  Snippet: {html[:1500]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(3)

# --- Approach 3: Try Angi ---
print("\n=== Angi Direct ===")
try:
    url = 'https://www.angi.com/companylist/vancouver/bathroom-remodel.htm'
    html = fetch(url)
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)', html)
    print(f"  Found {len(names)} names")
    for i, name in enumerate(names[:10]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        print(f"  {i+1}. {name} | Rating: {r}")
    if not names:
        print(f"  HTML length: {len(html)}")
        # Check for redirect or block
        if len(html) < 500:
            print(f"  Full: {html}")
        else:
            print(f"  Snippet: {html[:1000]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(3)

# --- Approach 4: Try BBB ---
print("\n=== BBB Direct ===")
try:
    url = 'https://www.bbb.org/search?find_country=US&find_latlng=45.6387%2C-122.5962&find_loc=Vancouver%2C%20WA&find_text=bathroom%20remodeling&find_type=Category&page=1&sort=Relevance'
    html = fetch(url)
    names = re.findall(r'data-testid="[^"]*name[^"]*"[^>]*>(.*?)<', html)
    if not names:
        names = re.findall(r'class="[^"]*business-name[^"]*"[^>]*>(.*?)<', html)
    if not names:
        names = re.findall(r'"name"\s*:\s*"([^"]{5,80})"', html)
    print(f"  Found {len(names)} results")
    for i, n in enumerate(names[:10]):
        clean = re.sub(r'<[^>]+>', '', n).strip()
        if clean:
            print(f"  {i+1}. {clean}")
    if not names:
        print(f"  HTML length: {len(html)}")
        print(f"  Snippet: {html[:1000]}")
except Exception as e:
    print(f"  Error: {e}")
