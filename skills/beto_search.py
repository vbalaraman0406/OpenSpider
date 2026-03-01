import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

searches = [
    ('DuckDuckGo', 'https://html.duckduckgo.com/html/?q=Beto+%26+Son+contractor+Vancouver+WA+reviews+rating'),
    ('Brave', 'https://search.brave.com/search?q=Beto+and+Son+contractor+Vancouver+WA+bathroom+remodel'),
    ('Google', 'https://www.google.com/search?q=%22Beto+and+Son%22+contractor+Vancouver+WA'),
]

for name, url in searches:
    print(f'\n=== {name} ===')
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        html = r.text
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        beto_mentions = re.findall(r'.{0,80}[Bb]eto.{0,150}', text)
        if beto_mentions:
            print(f'Found {len(beto_mentions)} mentions:')
            for m in beto_mentions[:5]:
                print(f'  -> {m.strip()[:250]}')
        else:
            print(f'No Beto mentions. Length: {len(text)}')
            if len(text) > 50:
                print(f'Sample: {text[:300]}')
    except Exception as e:
        print(f'Error: {e}')

# Try Yelp search
print('\n=== Yelp Search ===')
try:
    r = requests.get('https://www.yelp.com/search?find_desc=Beto+and+Son&find_loc=Vancouver+WA+98662', headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    beto = re.findall(r'.{0,80}[Bb]eto.{0,150}', text)
    if beto:
        for m in beto[:3]:
            print(m.strip()[:250])
    else:
        print(f'No results. Status: {r.status_code}, Length: {len(text)}')
except Exception as e:
    print(f'Error: {e}')
