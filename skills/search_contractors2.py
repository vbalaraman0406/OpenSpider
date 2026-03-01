import urllib.request
import urllib.parse
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Try DuckDuckGo lite
query = "bathroom tile vanity contractor Vancouver WA 98662"
url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Print first 2000 chars to understand structure
    print("=== DDG LITE ===")
    # Extract links
    links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*class="result-link"[^>]*>(.*?)</a>', html, re.DOTALL)
    if not links:
        links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    for l in links[:20]:
        clean = re.sub(r'<[^>]+>', '', l[1]).strip()
        if clean and 'duckduckgo' not in l[0]:
            print(f"{clean} -> {l[0]}")
except Exception as e:
    print(f"DDG Lite error: {e}")

# Try Yelp directly
print("\n=== YELP DIRECT ===")
yelp_url = "https://www.yelp.com/search?find_desc=bathroom+tile+vanity+contractor&find_loc=Vancouver%2C+WA+98662"
req2 = urllib.request.Request(yelp_url, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    html2 = resp2.read().decode('utf-8', errors='ignore')
    # Look for business names and ratings
    # Yelp uses structured data
    biz_names = re.findall(r'"name"\s*:\s*"([^"]+)"', html2)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html2)
    phones = re.findall(r'"telephone"\s*:\s*"([^"]+)"', html2)
    
    # Also try alt patterns
    alt_names = re.findall(r'class="css-[^"]*"[^>]*>\s*<a[^>]*href="/biz/([^"]+)"[^>]*>(.*?)</a>', html2, re.DOTALL)
    
    print(f"Biz names from JSON-LD: {biz_names[:10]}")
    print(f"Ratings: {ratings[:10]}")
    print(f"Phones: {phones[:10]}")
    print(f"Alt names: {len(alt_names)}")
    
    # Try to find business cards
    cards = re.findall(r'/biz/([a-z0-9-]+(?:-vancouver)?[a-z0-9-]*)', html2)
    unique_cards = list(dict.fromkeys(cards))[:10]
    print(f"Biz slugs: {unique_cards}")
    
except Exception as e:
    print(f"Yelp error: {e}")

# Try Google
print("\n=== GOOGLE ===")
google_url = f"https://www.google.com/search?q={urllib.parse.quote('best bathroom tile contractor Vancouver WA 98662 reviews rating')}"
req3 = urllib.request.Request(google_url, headers=headers)
try:
    resp3 = urllib.request.urlopen(req3, timeout=15)
    html3 = resp3.read().decode('utf-8', errors='ignore')
    # Extract snippets
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html3, re.DOTALL)
    for t in titles[:10]:
        clean = re.sub(r'<[^>]+>', '', t).strip()
        print(f"Title: {clean}")
except Exception as e:
    print(f"Google error: {e}")
