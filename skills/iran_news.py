import requests
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings('ignore')

queries = [
    'Iran US war latest news today 2026',
    'Iran conflict military update March 2026',
    'Iran US diplomatic negotiations 2026',
    'Strait of Hormuz shipping update 2026'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

seen_titles = set()

for q in queries:
    print(f'\n=== QUERY: {q} ===')
    url = f'https://news.google.com/rss/search?q={q.replace(" ", "+")}&hl=en-US&gl=US&ceid=US:en'
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        root = ET.fromstring(resp.text)
        items = root.findall('.//item')
        count = 0
        for item in items:
            if count >= 6:
                break
            title = item.find('title').text if item.find('title') is not None else 'N/A'
            if title in seen_titles:
                continue
            seen_titles.add(title)
            link = item.find('link').text if item.find('link') is not None else 'N/A'
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else 'N/A'
            source_el = item.find('source')
            source = source_el.text if source_el is not None else 'N/A'
            print(f'[{source}] {title}')
            print(f'  Date: {pubdate}')
            count += 1
    except Exception as e:
        print(f'Error: {e}')
