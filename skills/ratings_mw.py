import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Google Maps / Google Business via search
queries = [
    'Mountainwood+Homes+Vancouver+WA+reviews',
    'Mountainwood+Homes+Portland+OR+reviews+rating',
    'site:yelp.com+Mountainwood+Homes'
]

for q in queries:
    try:
        url = f'https://html.duckduckgo.com/html/?q={q}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.select('.result')
        print(f'\n=== Query: {q} ===')
        for res in results[:5]:
            title = res.select_one('.result__title')
            snippet = res.select_one('.result__snippet')
            link = res.select_one('.result__url')
            t = title.get_text(strip=True) if title else ''
            s = snippet.get_text(strip=True) if snippet else ''
            l = link.get_text(strip=True) if link else ''
            print(f'Title: {t}')
            print(f'URL: {l}')
            print(f'Snippet: {s}')
            # Look for rating patterns
            rating_match = re.findall(r'(\d\.\d)\s*(?:star|rating|out of|/5)', s, re.I)
            review_match = re.findall(r'(\d+)\s*(?:review|rating)', s, re.I)
            if rating_match:
                print(f'  >> RATING FOUND: {rating_match}')
            if review_match:
                print(f'  >> REVIEWS FOUND: {review_match}')
            print()
    except Exception as e:
        print(f'Error for {q}: {e}')

# Try Houzz page
try:
    r = requests.get('https://www.houzz.com/professionals/general-contractors/mountainwood-homes-pfvwus-pf~1947498053', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for rating
    rating_els = soup.find_all(string=re.compile(r'\d\.\d'))
    review_els = soup.find_all(string=re.compile(r'\d+\s*review', re.I))
    print('\n=== HOUZZ ===')
    print(f'Rating elements: {[r.strip() for r in rating_els[:5]]}')
    print(f'Review elements: {[r.strip() for r in review_els[:5]]}')
except Exception as e:
    print(f'Houzz error: {e}')

# Try BBB
try:
    url = 'https://html.duckduckgo.com/html/?q=site:bbb.org+Mountainwood+Homes'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.select('.result')
    print('\n=== BBB ===')
    for res in results[:3]:
        title = res.select_one('.result__title')
        snippet = res.select_one('.result__snippet')
        t = title.get_text(strip=True) if title else ''
        s = snippet.get_text(strip=True) if snippet else ''
        print(f'Title: {t}')
        print(f'Snippet: {s}\n')
except Exception as e:
    print(f'BBB error: {e}')

# Try Google Business Profile via search
try:
    url = 'https://html.duckduckgo.com/html/?q=Mountainwood+Homes+google+reviews+rating+stars'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.select('.result')
    print('\n=== Google Reviews Search ===')
    for res in results[:5]:
        title = res.select_one('.result__title')
        snippet = res.select_one('.result__snippet')
        t = title.get_text(strip=True) if title else ''
        s = snippet.get_text(strip=True) if snippet else ''
        print(f'Title: {t}')
        print(f'Snippet: {s}\n')
except Exception as e:
    print(f'Google reviews search error: {e}')
