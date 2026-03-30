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
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36','Accept':'text/html'}, timeout=15)
        p = TP()
        p.feed(r.text[:80000])
        return p.texts
    except Exception as e:
        return [str(e)]

kw = ['bank','financ','breach','hack','ransom','occ','ffiec','credit union','fintech','payment','fraud','cyber','zero-day','cve','patch','vulnerab']

sources = [
    ('CISA Alerts','https://www.cisa.gov/news-events/cybersecurity-advisories'),
    ('SecurityWeek','https://www.securityweek.com/'),
    ('KrebsOnSecurity','https://krebsonsecurity.com/'),
    ('BankInfoSec','https://www.bankinfosecurity.com/'),
    ('SC Magazine','https://www.scworld.com/news'),
]

for name, url in sources:
    print(f'\n=== {name} ===')
    texts = get_text(url)
    relevant = [t[:200] for t in texts if any(k in t.lower() for k in kw)]
    for r in relevant[:8]:
        print(f'  >> {r}')
    print(f'--- Headlines ---')
    for t in texts[:25]:
        if 15 < len(t) < 300:
            print(f'  {t}')

print('\nDONE')
