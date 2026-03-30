import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def clean(t):
    t = re.sub(r'&#\d+;', '', t)
    t = re.sub(r'&#91;.*?&#93;', '', t)
    return re.sub(r'<[^>]+>', '', t).strip()

url = 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Tamil_Nadu_Legislative_Assembly_election'
r = requests.get(url, headers=headers, timeout=15)
html = r.text
rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
print(f'Total rows: {len(rows)}')
for i in range(min(len(rows), 80)):
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', rows[i], re.DOTALL)
    cells = [clean(c) for c in cells]
    line = ' | '.join(c for c in cells[:12] if c)
    if line and len(line) > 3:
        print(f'R{i}: {line}')
