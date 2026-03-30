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

# Source 1: Google News search
try:
    url = 'https://www.google.com/search?q=Tamil+Nadu+election+2026+latest+news&tbm=nws&num=10'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 40 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'Google News'})
            if len(articles) >= 8:
                break
    results['google_news'] = articles
    print('Google News: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('Google News error: ' + str(e))
    results['google_news'] = []

time.sleep(2)

# Source 2: NDTV
try:
    url = 'https://www.ndtv.com/search?searchtext=Tamil+Nadu+election+2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        href = a.get('href', '')
        if len(text) > 30 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'NDTV'})
            if len(articles) >= 5:
                break
    results['ndtv'] = articles
    print('NDTV: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('NDTV error: ' + str(e))
    results['ndtv'] = []

time.sleep(2)

# Source 3: India Today
try:
    url = 'https://www.indiatoday.in/search/Tamil+Nadu+election+2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 30 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'India Today'})
            if len(articles) >= 5:
                break
    results['india_today'] = articles
    print('India Today: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('India Today error: ' + str(e))
    results['india_today'] = []

time.sleep(2)

# Source 4: The Hindu
try:
    url = 'https://www.thehindu.com/search/?q=Tamil+Nadu+election+2026&order=DESC&sort=publishdate'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 30 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'The Hindu'})
            if len(articles) >= 5:
                break
    results['the_hindu'] = articles
    print('The Hindu: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('The Hindu error: ' + str(e))
    results['the_hindu'] = []

time.sleep(2)

# Source 5: Times of India
try:
    url = 'https://timesofindia.indiatimes.com/topic/tamil-nadu-election-2026'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        if len(text) > 30 and ('tamil' in text.lower() or 'election' in text.lower() or 'dmk' in text.lower()):
            articles.append({'title': text[:200], 'source': 'TOI'})
            if len(articles) >= 5:
                break
    results['toi'] = articles
    print('TOI: Found ' + str(len(articles)) + ' articles')
except Exception as e:
    print('TOI error: ' + str(e))
    results['toi'] = []

time.sleep(2)

# Source 6: Google search for opinion polls
try:
    url = 'https://www.google.com/search?q=Tamil+Nadu+2026+election+opinion+poll+seat+prediction+DMK+AIADMK+BJP'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for div in soup.find_all('div'):
        text = div.get_text(strip=True)
        if len(text) > 50 and len(text) < 500 and ('seat' in text.lower() or 'poll' in text.lower() or 'predict' in text.lower()):
            if text not in snippets:
                snippets.append(text)
            if len(snippets) >= 5:
                break
    results['opinion_polls'] = snippets
    print('Opinion polls: Found ' + str(len(snippets)) + ' snippets')
except Exception as e:
    print('Opinion polls error: ' + str(e))
    results['opinion_polls'] = []

with open('tn_election_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print('\n=== SUMMARY ===')
for source, data in results.items():
    print(source + ': ' + str(len(data)) + ' items')
