import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

queries = [
    'Tamil Nadu 2026 election India Today latest news',
    'Tamil Nadu 2026 election Times of India opinion poll',
    'Tamil Nadu 2026 election opinion poll seat prediction DMK AIADMK BJP TVK',
    'Tamil Nadu election 2026 NDTV',
    'Tamil Nadu 2026 election The Hindu',
    'Tamil Nadu election 2026 TVK NTK Vijay Seeman alliance'
]

for q in queries:
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(q)}&num=10'
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
        clean = lambda t: re.sub(r'<[^>]+>', '', t).strip()
        titles = [clean(t) for t in titles if len(clean(t)) > 10][:6]
        snippets = re.findall(r'class="BNeawe s3v9rd AP7Wnd"[^>]*><div[^>]*><div[^>]*>(.*?)</div>', html)
        snippets = [clean(s) for s in snippets if len(clean(s)) > 30][:5]
        if not snippets:
            snippets = re.findall(r'<span[^>]*>(.*?)</span>', html)
            snippets = [clean(s) for s in snippets if len(clean(s)) > 50][:5]
        print(f'\n=== {q} ===')
        for t in titles:
            print(f'TITLE: {t}')
        for s in snippets:
            print(f'SNIP: {s}')
    except Exception as e:
        print(f'ERROR for {q}: {e}')
