import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Try specific articles
urls = [
    ('Matrize-IANS', 'https://www.indiatoday.in/india/story/tamil-nadu-election-2026-opinion-poll-2696123-2025-03-15'),
    ('ET', 'https://economictimes.indiatimes.com/news/elections/assembly-elections/tamil-nadu'),
    ('DeccanHerald', 'https://www.deccanherald.com/elections/tamil-nadu-assembly-election'),
    ('Polymarket', 'https://polymarket.com/event/tamil-nadu-2026'),
    ('Metaculus', 'https://www.metaculus.com/questions/?search=tamil+nadu+2026'),
]

for name, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        print(f'[{name}] {text[:600]}')
    except Exception as e:
        print(f'[{name}] Error: {e}')
    print('---')

# Try Wikipedia opinion polling page
try:
    r = requests.get('https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Tamil_Nadu_Legislative_Assembly_election', headers=headers, timeout=10)
    if r.status_code == 200:
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Search for seat numbers
        for kw in ['seats', 'DMK', 'AIADMK', 'NDA', 'INDIA', 'TVK']:
            idx = text.lower().find(kw.lower())
            if idx > 0:
                print(f'[WikiPolls-{kw}] {text[max(0,idx-50):idx+200]}')
    else:
        print(f'WikiPolls: Status {r.status_code}')
except Exception as e:
    print(f'WikiPolls error: {e}')
