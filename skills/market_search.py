import urllib.request
import ssl
from html.parser import HTMLParser

ssl._create_default_https_context = ssl._create_unverified_context

class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_result = False
        self.in_snippet = False
        self.current = {}
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'result__a' in attrs_dict.get('class', ''):
            self.in_result = True
            self.current = {'title': '', 'url': attrs_dict.get('href', '')}
        if tag == 'a' and 'result__snippet' in attrs_dict.get('class', ''):
            self.in_snippet = True
            
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_result:
            self.in_result = False
        if tag == 'a' and self.in_snippet:
            self.in_snippet = False
            self.results.append(self.current)
            self.current = {}
            
    def handle_data(self, data):
        if self.in_result:
            self.current['title'] = self.current.get('title', '') + data
        if self.in_snippet:
            self.current['snippet'] = self.current.get('snippet', '') + data

searches = [
    'https://html.duckduckgo.com/html/?q=stock+market+Iran+war+reaction+March+2026+S%26P+500+oil+prices',
    'https://html.duckduckgo.com/html/?q=defense+stocks+LMT+RTX+NOC+Iran+conflict+March+2026',
    'https://html.duckduckgo.com/html/?q=oil+prices+gold+prices+Iran+attack+March+2026',
]

all_results = []
for url in searches:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        parser = DDGParser()
        parser.feed(html)
        all_results.extend(parser.results[:5])
    except Exception as e:
        print(f'Error: {e}')

print(f'Found {len(all_results)} results')
for i, r in enumerate(all_results):
    print(f"\n--- Result {i+1} ---")
    print(f"Title: {r.get('title', 'N/A')}")
    print(f"Snippet: {r.get('snippet', 'N/A')[:250]}")
