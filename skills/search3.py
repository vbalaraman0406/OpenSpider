import urllib.request
import urllib.parse
import re

queries = [
    "bathroom remodel contractor Vancouver WA",
    "bathroom tile contractor Vancouver Washington",
    "bathroom renovation Vancouver WA 98662"
]

all_text = ""

for q in queries:
    url = "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\n=== Query: {q} ===")
        print(f"HTML length: {len(html)}")
        # Extract text between result links
        # DDG lite uses <a> tags and <td> for snippets
        snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
        links = re.findall(r'<a[^>]*rel="nofollow"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        print(f"Snippets found: {len(snippets)}")
        print(f"Links found: {len(links)}")
        for i, (href, title) in enumerate(links[:15]):
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            print(f"  [{i+1}] {title_clean}")
            print(f"      URL: {href}")
        for i, s in enumerate(snippets[:15]):
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            print(f"  Snippet {i+1}: {s_clean[:200]}")
        all_text += html
    except Exception as e:
        print(f"Error for '{q}': {e}")

# Also try to find ratings/phone numbers in all collected text
phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', all_text)
ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of|/5)', all_text, re.IGNORECASE)
print(f"\nPhones found in all text: {phones[:20]}")
print(f"Ratings found in all text: {ratings[:20]}")
