import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Try Bing search
query = "Let's+Remodel+contractor+Vancouver+WA+bathroom+reviews+rating+phone"
url = f'https://www.bing.com/search?q={query}'
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract search result snippets
    # Look for <li class="b_algo"> blocks
    results = re.findall(r'<li class="b_algo">(.*?)</li>', html, re.DOTALL)
    print(f"Found {len(results)} Bing results")
    for i, r in enumerate(results[:8]):
        title = re.findall(r'<h2>(.*?)</h2>', r, re.DOTALL)
        title_text = re.sub(r'<[^>]+>', '', title[0]).strip() if title else 'N/A'
        links = re.findall(r'href="(https?://[^"]+)"', r)
        link = links[0] if links else 'N/A'
        snippet = re.findall(r'<p>(.*?)</p>', r, re.DOTALL)
        snippet_text = re.sub(r'<[^>]+>', '', snippet[0]).strip() if snippet else ''
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {title_text}")
        print(f"URL: {link}")
        print(f"Snippet: {snippet_text[:300]}")
except Exception as e:
    print(f"Bing search error: {e}")

# Also try searching their specific website
print("\n\n=== Trying direct website search ===")
for domain in ['letsremodel.com', 'letsremodeling.com', 'letsremodel.net']:
    try:
        url2 = f'https://www.{domain}/'
        req2 = urllib.request.Request(url2, headers=headers)
        resp2 = urllib.request.urlopen(req2, timeout=10)
        html2 = resp2.read().decode('utf-8', errors='ignore')
        title = re.findall(r'<title>(.*?)</title>', html2, re.IGNORECASE)
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html2)
        print(f"\n{domain} - FOUND!")
        print(f"Title: {title[0] if title else 'N/A'}")
        print(f"Phones: {list(set(phones))[:5]}")
        # Look for rating/review info
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', html2, re.IGNORECASE)
        print(f"Ratings found: {ratings}")
    except Exception as e:
        print(f"{domain} - Error: {e}")
