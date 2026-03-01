import requests
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    "Let's Remodel bathroom contractor Vancouver WA 98662",
    "Let's Remodel Vancouver WA",
    "letsremodel.com Vancouver WA",
    '"Let\'s Remodel" contractor Vancouver Washington'
]

for q in queries:
    print(f"\n=== Searching: {q} ===")
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = soup.select('.result')
        if not results:
            print("  No results found")
        for i, r in enumerate(results[:5]):
            title_el = r.select_one('.result__title a, .result__a')
            snippet_el = r.select_one('.result__snippet')
            url_el = r.select_one('.result__url')
            title = title_el.get_text(strip=True) if title_el else 'N/A'
            snippet = snippet_el.get_text(strip=True) if snippet_el else 'N/A'
            link = url_el.get_text(strip=True) if url_el else 'N/A'
            print(f"  [{i+1}] {title}")
            print(f"      URL: {link}")
            print(f"      Snippet: {snippet[:250]}")
    except Exception as e:
        print(f"  Error: {e}")
