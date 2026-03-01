import urllib.request
import re
import html

# We know these contractors from the Yelp snippet and other results:
# 1. Reliable Men Construction
# 2. NW Tub & Shower
# 3. Elegant Tile and Hardwood Floors
# 4. EcoCraft LLC
# 5. RTA Construction
# 6. Clean Cut Renovations
# 7. Salcans Construction
# 8. Neil Kelly

# Let's search for each one individually to get phone, website, rating
contractors = [
    'Reliable Men Construction Vancouver WA phone rating',
    'NW Tub and Shower Vancouver WA phone rating',
    'Elegant Tile and Hardwood Floors Vancouver WA phone rating',
    'EcoCraft LLC Vancouver WA bathroom contractor phone',
    'RTA Construction Vancouver WA bathroom phone rating',
    'Clean Cut Renovations Vancouver WA bathroom phone',
    'Salcans Construction Vancouver WA phone rating',
]

for q in contractors:
    query = q.replace(' ', '+')
    url = f'https://html.duckduckgo.com/html/?q={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8', errors='ignore')
        # Extract snippets
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', data, re.DOTALL)
        titles = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', data, re.DOTALL)
        print(f'\n=== {q} ===')
        for i, (href, title) in enumerate(titles[:3]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_title = html.unescape(clean_title)
            print(f'  Title: {clean_title}')
            print(f'  URL: {href}')
            if i < len(snippets):
                clean_snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                clean_snip = html.unescape(clean_snip)
                print(f'  Snippet: {clean_snip[:300]}')
    except Exception as e:
        print(f'Error for {q}: {e}')
