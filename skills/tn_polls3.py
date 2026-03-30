import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    ('NDTV', 'https://www.ndtv.com/topic/tamil-nadu-election-2026'),
    ('IndiaToday', 'https://www.indiatoday.in/elections/tamil-nadu'),
    ('News18', 'https://www.news18.com/elections/tamil-nadu-assembly-election/'),
    ('TheHindu', 'https://www.thehindu.com/elections/tamil-nadu-assembly/'),
    ('HT', 'https://www.hindustantimes.com/topic/tamil-nadu-election-2026'),
]

for name, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Find relevant snippets about polls/seats/predictions
        keywords = ['opinion poll', 'seat predict', 'survey', 'who will win', 'DMK.*seat', 'AIADMK.*seat', 'TVK', 'Vijay.*party', 'Matrize', 'exit poll']
        found = False
        for kw in keywords:
            for m in re.finditer(kw, text, re.IGNORECASE):
                start = max(0, m.start()-80)
                end = min(len(text), m.end()+150)
                snippet = text[start:end].strip()
                if len(snippet) > 30:
                    print(f'[{name}] {snippet}')
                    found = True
                    break
        if not found:
            # Just print first 500 chars of content
            print(f'[{name}] HEADLINES: {text[:500]}')
    except Exception as e:
        print(f'[{name}] Error: {e}')
    print('---')

# Try Matrize IANS poll specifically
try:
    r = requests.get('https://www.google.com/search?q=Matrize+IANS+Tamil+Nadu+2026+opinion+poll+seats', headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    print(f'[Matrize search] {text[:800]}')
except Exception as e:
    print(f'Matrize search error: {e}')
