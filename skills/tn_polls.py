import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

# Try opinion polling page first
for url in [
    'https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Tamil_Nadu_Legislative_Assembly_election',
    'https://en.wikipedia.org/wiki/2026_Tamil_Nadu_Legislative_Assembly_election'
]:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text
        tables = re.findall(r'<table[^>]*class="wikitable[^"]*"[^>]*>(.*?)</table>', html, re.DOTALL)
        print(f'URL: {url}')
        print(f'Found {len(tables)} wikitables')
        for i, table in enumerate(tables[:10]):
            rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
            print(f'\nTable {i+1} ({len(rows)} rows):')
            for row in rows[:20]:
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
                cleaned = [re.sub(r'<[^>]+>', '', c).strip()[:40] for c in cells]
                if any(cleaned):
                    print(' | '.join(cleaned))
        print('---END---')
    except Exception as e:
        print(f'Error: {e}')
