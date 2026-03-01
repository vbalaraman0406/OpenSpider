import urllib.request
import urllib.parse
import json
import re
from html.parser import HTMLParser

class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_result = False
        self.in_title = False
        self.in_snippet = False
        self.current = {}
        self.depth = 0
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        if tag == 'div' and 'result' in cls and 'results' not in cls:
            self.in_result = True
            self.current = {'title': '', 'url': '', 'snippet': ''}
        if self.in_result and tag == 'a' and 'result__a' in cls:
            self.in_title = True
            href = attrs_dict.get('href', '')
            if 'uddg=' in href:
                m = re.search(r'uddg=([^&]+)', href)
                if m:
                    self.current['url'] = urllib.parse.unquote(m.group(1))
            else:
                self.current['url'] = href
        if self.in_result and tag == 'a' and 'result__snippet' in cls:
            self.in_snippet = True
    def handle_data(self, data):
        if self.in_title:
            self.current['title'] += data
        if self.in_snippet:
            self.current['snippet'] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_title:
            self.in_title = False
        if tag == 'a' and self.in_snippet:
            self.in_snippet = False
        if tag == 'div' and self.in_result and self.current.get('title'):
            self.results.append(self.current)
            self.in_result = False

def search_ddg(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        parser = DDGParser()
        parser.feed(html)
        return parser.results
    except Exception as e:
        print(f'Search error: {e}')
        return []

queries = [
    'best bathroom remodel contractors Vancouver WA 98662 ratings reviews',
    'bathroom tile vanity replacement contractor Vancouver WA reviews phone',
    'top rated bathroom renovation company Vancouver Washington phone number',
    'site:thumbtack.com bathroom remodel Vancouver WA'
]

all_results = []
for q in queries:
    results = search_ddg(q)
    print(f'Query: {q}')
    print(f'Found {len(results)} results')
    for r in results:
        print(f"  Title: {r['title'][:80]}")
        print(f"  URL: {r['url'][:100]}")
        print(f"  Snippet: {r['snippet'][:150]}")
        print()
    all_results.extend(results)

print(f'\nTotal results: {len(all_results)}')
