import requests
from bs4 import BeautifulSoup
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

results = {}

# Load existing results
try:
    with open('tn_election_results.json', 'r') as f:
        results = json.load(f)
except:
    pass

# Source: DuckDuckGo search (less blocking than Google)
try:
    url = 'https://html.duckduckgo.com/html/?q=Tamil+Nadu+election+2026+latest+news'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for result in soup.find_all('div', class_='result')[:10]:
        title_el = result.find('a', class_='result__a')
        snippet_el = result.find('a', class_='result__snippet')
        title = title_el.get_text(strip=True) if title_el else ''
        snippet = snippet_el.get_text(strip=True) if snippet_el else ''
        if title and len(title) > 15:
            articles.append({'title': title[:200], 'snippet': snippet[:300], 'source': 'DuckDuckGo'})
    results['duckduckgo'] = articles
    print('DuckDuckGo: Found ' + str(len(articles)) + ' results')
except Exception as e:
    print('DuckDuckGo error: ' + str(e))

time.sleep(2)

# Source: News18
try:
    url = 'https://www.news18.com/topics/tamil-nadu-elections/'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 35 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower() or 'aiadmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'News18'})
            if len(articles) >= 5:
                break
    results['news18'] = articles
    print('News18: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('News18 error: ' + str(e))

time.sleep(2)

# Source: Deccan Herald
try:
    url = 'https://www.deccanherald.com/search?q=Tamil+Nadu+election+2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 35 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'Deccan Herald'})
            if len(articles) >= 5:
                break
    results['deccan_herald'] = articles
    print('Deccan Herald: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('Deccan Herald error: ' + str(e))

time.sleep(2)

# Source: Scroll.in
try:
    url = 'https://scroll.in/search?q=Tamil+Nadu+election+2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 35 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'Scroll.in'})
            if len(articles) >= 5:
                break
    results['scroll'] = articles
    print('Scroll.in: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('Scroll.in error: ' + str(e))

time.sleep(2)

# Source: Bing News
try:
    url = 'https://www.bing.com/news/search?q=Tamil+Nadu+election+2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 35 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower() or 'aiadmk' in text.lower() or 'bjp' in text.lower()):
            articles.append({'title': text[:200], 'source': 'Bing News'})
            if len(articles) >= 8:
                break
    results['bing_news'] = articles
    print('Bing News: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('Bing News error: ' + str(e))

with open('tn_election_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print('\n=== FINAL SUMMARY ===')
total = 0
for source, data in results.items():
    count = len(data)
    total += count
    print(source + ': ' + str(count) + ' items')
print('Total: ' + str(total) + ' items')
