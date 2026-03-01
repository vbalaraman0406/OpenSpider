import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try BizProfile
try:
    r = requests.get('https://www.bizprofile.com/company/beto-and-son-remodeling-llc-vancouver-wa', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)[:2000]
    print('=== BIZPROFILE ===')
    print(text[:1500])
except Exception as e:
    print(f'BizProfile error: {e}')

print('\n')

# Try Thumbtack
try:
    r = requests.get('https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/', headers=headers, timeout=10)
    if 'Beto' in r.text:
        idx = r.text.lower().find('beto')
        print('=== THUMBTACK ===')
        print(r.text[max(0,idx-200):idx+500])
    else:
        print('Beto not found on Thumbtack listing page')
except Exception as e:
    print(f'Thumbtack error: {e}')

print('\n')

# Try Brave search for Google rating specifically
try:
    r = requests.get('https://search.brave.com/search?q=Beto+and+Son+Remodeling+LLC+Vancouver+WA+google+rating+stars+reviews', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for rating snippets
    for snippet in soup.find_all(['span', 'div'], string=lambda t: t and ('star' in t.lower() or 'rating' in t.lower() or '4.' in t or '5.' in t)):
        print(f'Rating snippet: {snippet.get_text()}')
    # Get all snippet text
    snippets = soup.find_all('div', class_='snippet-description')
    for s in snippets[:5]:
        txt = s.get_text(' ', strip=True)
        if any(w in txt.lower() for w in ['beto', 'rating', 'review', 'star']):
            print(f'Snippet: {txt[:300]}')
    # Also check result titles and descriptions
    results = soup.find_all('a', class_='result-header')
    for r2 in results[:8]:
        print(f'Result: {r2.get_text()} -> {r2.get("href", "")}')
except Exception as e:
    print(f'Brave error: {e}')

print('\n')

# Try HomeYou
try:
    r = requests.get('https://search.brave.com/search?q=%22Beto+and+Son+Remodeling%22+site:homeyou.com', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if 'homeyou.com' in a['href'] and 'beto' in a['href'].lower():
            print(f'HomeYou URL: {a["href"]}')
            # Try to fetch it
            r2 = requests.get(a['href'], headers=headers, timeout=10)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            text2 = soup2.get_text(' ', strip=True)[:1500]
            print(text2[:1000])
            break
except Exception as e:
    print(f'HomeYou error: {e}')
