import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

pages = [
    ('Sprint Qualifying', 'https://www.crash.net/f1/results/1091172/1/2026-f1-chinese-grand-prix-full-results-and-times-sprint-qualifying'),
    ('FP1', 'https://www.crash.net/f1/results/1091170/1/2026-f1-chinese-grand-prix-full-results-and-times-fp1'),
]

drivers = ['Verstappen', 'Piastri', 'Norris', 'Hamilton', 'Leclerc', 'Sainz', 'Russell', 'Bearman', 'Hadjar', 'Perez', 'Alonso', 'Stroll', 'Gasly', 'Doohan', 'Lawson', 'Tsunoda', 'Hulkenberg', 'Bortoleto', 'Antonelli', 'Colapinto']

for name, url in pages:
    try:
        resp = session.get(url, timeout=15)
        html = resp.text
        
        # Try to find table elements
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
        print(f'\n===== {name} =====')
        print(f'Tables found: {len(tables)}')
        
        for ti, table in enumerate(tables):
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
            if len(rows) > 5:  # Likely a results table
                print(f'\nTable {ti} ({len(rows)} rows):')
                for row in rows[:22]:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
                    cell_texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    cell_texts = [c for c in cell_texts if c]  # Remove empty
                    if cell_texts:
                        print('  | '.join(cell_texts))
        
        # Also try extracting from the full text
        text = re.sub(r'<[^>]+>', '\n', html)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Find lines with driver names and nearby lines
        print(f'\nDriver mentions in text:')
        for i, line in enumerate(lines):
            if any(d in line for d in drivers):
                context = lines[max(0,i-1):min(len(lines),i+3)]
                print(f'  {" | ".join(context)}')
    except Exception as e:
        print(f'Error: {name}: {e}')
