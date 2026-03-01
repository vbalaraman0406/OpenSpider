import requests
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try various search queries
queries = [
    'Mountainwood Vancouver WA contractor',
    '"Mountain Wood" bathroom remodel Vancouver WA',
    '"Mountainwood" Vancouver WA 98662',
    'Mountainwood LLC Vancouver Washington',
    'Mountainwood home improvement Vancouver WA',
    'Mountainwood Floors Vancouver WA',
]

for q in queries:
    print(f'\n=== SEARCH: {q} ===')
    try:
        url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = soup.select('.result__title')
        snippets = soup.select('.result__snippet')
        found_relevant = False
        for i, r in enumerate(results[:5]):
            title = r.get_text(strip=True)
            link_tag = r.find('a')
            link = link_tag.get('href','') if link_tag else ''
            snip = snippets[i].get_text(strip=True) if i < len(snippets) else ''
            if 'mountainwood' in title.lower() or 'mountainwood' in snip.lower() or 'mountain wood' in title.lower() or 'mountain wood' in snip.lower():
                found_relevant = True
                print(f'  MATCH: {title}')
                print(f'  Link: {link}')
                print(f'  Snippet: {snip[:200]}')
        if not found_relevant:
            print('  No relevant Mountainwood results found.')
    except Exception as e:
        print(f'  Error: {e}')

# Try Facebook search
print('\n=== FACEBOOK CHECK ===')
try:
    fb_url = 'https://www.facebook.com/search/pages/?q=Mountainwood%20Vancouver%20WA'
    print(f'  Facebook search URL (manual): {fb_url}')
except Exception as e:
    print(f'  Error: {e}')

# Try Google Maps embed search
print('\n=== GOOGLE MAPS CHECK ===')
try:
    gm_url = f'https://www.google.com/maps/search/Mountainwood+bathroom+remodel+Vancouver+WA+98662'
    print(f'  Google Maps URL (manual): {gm_url}')
except Exception as e:
    print(f'  Error: {e}')

# Try Nextdoor / Thumbtack / HomeAdvisor / Houzz
print('\n=== DIRECTORY CHECKS ===')
directories = [
    ('Thumbtack', f'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'),
    ('HomeAdvisor', f'https://www.homeadvisor.com/rated.Mountainwood.html'),
    ('Houzz', f'https://www.houzz.com/professionals/general-contractors/mountainwood-pfvwus-pf~1'),
]
for name, url in directories:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if 'mountainwood' in resp.text.lower() or 'mountain wood' in resp.text.lower():
            print(f'  {name}: FOUND mention of Mountainwood!')
            # Extract context
            idx = resp.text.lower().find('mountainwood')
            if idx == -1:
                idx = resp.text.lower().find('mountain wood')
            context = resp.text[max(0,idx-100):idx+200]
            print(f'  Context: {context[:300]}')
        else:
            print(f'  {name}: No mention found (status {resp.status_code})')
    except Exception as e:
        print(f'  {name}: Error - {e}')
