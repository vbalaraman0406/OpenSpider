import urllib.request
import urllib.parse
import re

contractors = [
    ('Reliable Men', 'Reliable Men contractor Vancouver WA bathroom remodel'),
    ('Lets Remodel', 'Lets Remodel contractor Vancouver WA'),
    ('Fazzolari', 'Fazzolari contractor Vancouver WA bathroom'),
    ('Mountainwood', 'Mountainwood contractor Vancouver WA'),
    ('Beto and Son', 'Beto and Son contractor Vancouver WA')
]

for name, query in contractors:
    print(f'\n=== {name} ===')
    try:
        url = 'https://lite.duckduckgo.com/lite/?q=' + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result links and snippets
        # DDG lite uses <a> tags with class="result-link"
        links = re.findall(r'<a[^>]*rel="nofollow"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html)
        if not links:
            links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>', html)
        # Also get snippets
        snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<span[^>]*class="link-text"[^>]*>(.*?)</span>', html, re.DOTALL)
        
        seen = set()
        count = 0
        for href, title in links:
            if 'duckduckgo' in href:
                continue
            if href not in seen:
                seen.add(href)
                print(f'  [{title.strip()}]({href})')
                count += 1
                if count >= 5:
                    break
        for i, s in enumerate(snippets[:3]):
            clean = re.sub(r'<[^>]+>', '', s).strip()
            if clean:
                print(f'  Snippet {i+1}: {clean[:200]}')
        if count == 0 and not snippets:
            print('  No results found')
            # dump first 500 chars for debug
            print('  HTML preview:', html[:300])
    except Exception as e:
        print(f'  Error: {e}')
