import re

with open('/Users/vbalaraman/OpenSpider/tn_search.html', 'r', errors='ignore') as f:
    html = f.read()

print(f'HTML length: {len(html)}')

# Extract result titles and URLs
titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
urls = re.findall(r'class="result__a"[^>]*href="([^"]+)"', html)
snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)

print(f'Results found: {len(titles)}')
for i in range(min(10, len(titles))):
    t = re.sub(r'<[^>]+>', '', titles[i]).strip()
    s = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:200] if i < len(snippets) else ''
    u = urls[i] if i < len(urls) else ''
    print(f'\n{i+1}. {t}')
    print(f'   Snippet: {s}')
    print(f'   URL: {u}')
