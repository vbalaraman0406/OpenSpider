import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

queries = [
    'bathroom remodel contractor Vancouver WA 98662 reviews',
    'bathroom tile vanity replacement Vancouver Washington contractor',
    'best bathroom renovation company Vancouver WA'
]

all_results = []

for q in queries:
    url = f'https://www.bing.com/search?q={requests.utils.quote(q)}'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'Query: {q[:50]}... Status: {r.status_code}')
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try multiple selectors for Bing results
        results = soup.select('li.b_algo')
        print(f'  Found {len(results)} results')
        
        for res in results:
            title_el = res.select_one('h2 a')
            snippet_el = res.select_one('.b_caption p') or res.select_one('p')
            if title_el:
                title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                snippet = snippet_el.get_text(strip=True) if snippet_el else ''
                all_results.append({'title': title, 'link': link, 'snippet': snippet})
                print(f'  - {title[:60]}')
    except Exception as e:
        print(f'Error: {e}')

print(f'\nTotal results: {len(all_results)}')

# Now extract contractor names and info from snippets
contractors = {}
for r in all_results:
    snippet = r['snippet']
    title = r['title']
    link = r['link']
    
    # Look for rating patterns
    rating_match = re.search(r'(\d\.\d)\s*(?:star|/5|rating|out of)', snippet, re.I)
    review_match = re.search(r'(\d+)\s*(?:review|rating)', snippet, re.I)
    
    rating = rating_match.group(1) if rating_match else ''
    reviews = review_match.group(1) if review_match else ''
    
    # Store unique results
    key = title[:40]
    if key not in contractors:
        contractors[key] = {
            'title': title,
            'link': link,
            'snippet': snippet[:200],
            'rating': rating,
            'reviews': reviews
        }

print('\n=== EXTRACTED DATA ===')
for k, v in contractors.items():
    print(f"Name: {v['title']}")
    print(f"Link: {v['link']}")
    print(f"Rating: {v['rating']} | Reviews: {v['reviews']}")
    print(f"Snippet: {v['snippet'][:150]}")
    print('---')
