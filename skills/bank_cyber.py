import requests
from html.parser import HTMLParser

class TP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip = False
    def handle_data(self, data):
        if not self.skip:
            t = data.strip()
            if len(t) > 10: self.texts.append(t)

def get_text(url):
    try:
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}, timeout=15)
        p = TP()
        p.feed(r.text[:40000])
        return p.texts
    except Exception as e:
        return [str(e)]

kw = ['bank','financ','breach','hack','ransom','occ','ffiec','credit union','fintech','payment','fraud','cyber']

sources = [
    ('BleepingComputer','https://www.bleepingcomputer.com/news/security/'),
    ('TheHackerNews','https://thehackernews.com/'),
    ('DarkReading','https://www.darkreading.com/threat-intelligence'),
]

for name, url in sources:
    print(f'\n=== {name} ===')
    texts = get_text(url)
    relevant = [t[:200] for t in texts if any(k in t.lower() for k in kw)]
    for r in relevant[:10]:
        print(f'  >> {r}')
    print(f'--- First 15 items ---')
    for t in texts[:15]:
        if 15 < len(t) < 250:
            print(f'  {t}')

print('\nDONE')
