import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Bing with different query
print('=== BING SEARCH 1 ===')
try:
    r = requests.get('https://www.bing.com/search?q=site:formula1.com+fantasy+2025', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for li in soup.find_all('li', class_='b_algo')[:8]:
        h2 = li.find('h2')
        if h2:
            a = h2.find('a')
            if a:
                print(f'Title: {h2.get_text(strip=True)}')
                print(f'URL: {a.get("href","")}')
                p = li.find('p')
                if p:
                    print(f'Snippet: {p.get_text(strip=True)[:300]}')
                print()
except Exception as e:
    print(f'Error: {e}')

print('\n=== BING SEARCH 2 ===')
try:
    r = requests.get('https://www.bing.com/search?q=%22f1+fantasy%22+2025+scoring+driver+prices+rules', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for li in soup.find_all('li', class_='b_algo')[:8]:
        h2 = li.find('h2')
        if h2:
            a = h2.find('a')
            if a:
                print(f'Title: {h2.get_text(strip=True)}')
                print(f'URL: {a.get("href","")}')
                p = li.find('p')
                if p:
                    print(f'Snippet: {p.get_text(strip=True)[:300]}')
                print()
except Exception as e:
    print(f'Error: {e}')

# Try fetching Grid Rivals
print('\n=== GRID RIVALS ===')
try:
    r = requests.get('https://gridrivals.com', headers=headers, timeout=10, allow_redirects=True)
    print(f'Status: {r.status_code}, URL: {r.url}')
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find('title')
    if title:
        print(f'Title: {title.get_text(strip=True)}')
    text = soup.get_text(separator=' ', strip=True)
    print(text[:500])
except Exception as e:
    print(f'Error: {e}')

# Try fetching the F1 official fantasy page
print('\n=== F1 FANTASY MAIN ===')
try:
    r = requests.get('https://fantasy.formula1.com/', headers=headers, timeout=10, allow_redirects=True)
    print(f'Status: {r.status_code}, URL: {r.url}')
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for meta tags with description
    for meta in soup.find_all('meta'):
        name = meta.get('name', '') or meta.get('property', '')
        content = meta.get('content', '')
        if content and len(content) > 20:
            print(f'{name}: {content}')
except Exception as e:
    print(f'Error: {e}')
