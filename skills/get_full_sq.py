import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

# Get Sprint Qualifying results - extract just positions 9-20
resp = session.get('https://www.crash.net/f1/results/1091172/1/2026-f1-chinese-grand-prix-full-results-and-times-sprint-qualifying', timeout=15)
html = resp.text

tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
for table in tables:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
    if len(rows) > 5:
        for i, row in enumerate(rows):
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            cell_texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            cell_texts = [c for c in cell_texts if c]
            if cell_texts and i >= 9:  # Skip header and top 8 (already have those)
                print(' | '.join(cell_texts))

print('\n--- FP1 Full Results ---')
resp2 = session.get('https://www.crash.net/f1/results/1091170/1/2026-f1-chinese-grand-prix-full-results-and-times-fp1', timeout=15)
html2 = resp2.text
tables2 = re.findall(r'<table[^>]*>(.*?)</table>', html2, re.DOTALL)
for table in tables2:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
    if len(rows) > 5:
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            cell_texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            cell_texts = [c for c in cell_texts if c]
            if cell_texts:
                print(' | '.join(cell_texts))
