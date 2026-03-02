import urllib.request
import urllib.parse
import json
import re
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip = False
        self.skip_tags = {'script', 'style', 'noscript'}
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip = True
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.texts.append(text)

def search_duckduckgo(query):
    encoded = urllib.parse.quote(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = []
        # Find result links and snippets
        pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        links = re.findall(pattern, html, re.DOTALL)
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        snippets = re.findall(snippet_pattern, html, re.DOTALL)
        
        for i, (link, title) in enumerate(links[:15]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = ''
            if i < len(snippets):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            # Decode DuckDuckGo redirect URL
            if 'uddg=' in link:
                actual = urllib.parse.unquote(link.split('uddg=')[1].split('&')[0])
            else:
                actual = link
            results.append({'title': clean_title, 'url': actual, 'snippet': clean_snippet})
        return results
    except Exception as e:
        return [{'error': str(e)}]

queries = [
    'best bathroom tile contractors installers reviews',
    'bathroom tile remodel contractors Yelp Angi HomeAdvisor',
    'top rated bathroom tile installation companies Thumbtack',
    'bathroom tile contractors near me ratings phone number'
]

all_results = []
for q in queries:
    print(f'\n=== Searching: {q} ===')
    results = search_duckduckgo(q)
    for r in results:
        if 'error' not in r:
            print(f"Title: {r['title']}")
            print(f"URL: {r['url']}")
            print(f"Snippet: {r['snippet'][:200]}")
            print('---')
    all_results.extend(results)

print(f'\nTotal results found: {len(all_results)}')
