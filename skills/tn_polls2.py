import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

searches = [
    'Tamil+Nadu+2026+election+opinion+poll+seat+prediction',
    'Tamil+Nadu+election+2026+survey+DMK+AIADMK+seats',
    'TVK+Vijay+Tamil+Nadu+2026+election+prediction',
    'Matrize+IANS+Tamil+Nadu+2026+poll',
    'Tamil+Nadu+2026+election+who+will+win'
]

for q in searches:
    try:
        url = f'https://www.google.com/search?q={q}'
        r = requests.get(url, headers=headers, timeout=10)
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text)
        # Find relevant snippets
        for kw in ['seats', 'poll', 'survey', 'predict', 'DMK', 'AIADMK', 'TVK', 'Vijay', 'Matrize']:
            idx = text.lower().find(kw.lower())
            while idx != -1 and idx < len(text):
                snippet = text[max(0,idx-100):idx+200]
                if len(snippet.strip()) > 20:
                    print(f'[{q[:30]}] ...{snippet.strip()}...')
                idx = text.lower().find(kw.lower(), idx+200)
                if idx > 5000:
                    break
    except Exception as e:
        print(f'Error: {e}')
    print('---')
