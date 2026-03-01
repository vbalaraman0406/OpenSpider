from bs4 import BeautifulSoup
import re, json

contractors = {}

for f in ['/tmp/bing1.html', '/tmp/bing2.html', '/tmp/bing3.html']:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
        soup = BeautifulSoup(fh.read(), 'html.parser')
    # Try multiple selectors
    results = soup.select('li.b_algo')
    if not results:
        results = soup.select('ol#b_results li')
    for r in results:
        title_el = r.select_one('h2 a') or r.select_one('h2')
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        url = title_el.get('href', '')
        snippet_el = r.select_one('.b_caption p') or r.select_one('p')
        snippet = snippet_el.get_text(strip=True) if snippet_el else ''
        # Extract rating patterns
        rating_match = re.search(r'(\d\.\d)\s*(?:star|/5|out of|rating)', snippet, re.I)
        rating = rating_match.group(1) if rating_match else ''
        review_match = re.search(r'(\d+)\s*(?:review|rating)', snippet, re.I)
        reviews = review_match.group(1) if review_match else ''
        # Skip aggregator pages, keep individual contractor mentions
        key = title[:60]
        if key not in contractors:
            contractors[key] = {'title': title, 'url': url, 'snippet': snippet[:200], 'rating': rating, 'reviews': reviews}

print(f'Found {len(contractors)} results')
for k, v in list(contractors.items())[:30]:
    print(f"\nTITLE: {v['title']}")
    print(f"URL: {v['url']}")
    print(f"RATING: {v['rating']} | REVIEWS: {v['reviews']}")
    print(f"SNIPPET: {v['snippet']}")
