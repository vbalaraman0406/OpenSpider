import requests
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Try direct website guesses
possible_urls = [
    'https://www.letsremodel.com',
    'https://letsremodel.com',
    'http://www.letsremodel.com',
    'https://www.letsremodel.net',
    'https://www.letsremodelwa.com',
]

print('=== Trying direct URLs ===')
for url in possible_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"  {url} -> Status: {resp.status_code}, Final URL: {resp.url}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else 'No title'
            print(f"    Title: {title}")
            # Look for phone numbers
            import re
            phones = re.findall(r'[\(]?\d{3}[\)]?[\s\-\.]?\d{3}[\s\-\.]?\d{4}', resp.text)
            if phones:
                print(f"    Phones found: {list(set(phones))[:5]}")
            # Look for address
            text = soup.get_text(' ', strip=True)[:3000]
            if 'Vancouver' in text or '98662' in text:
                print(f"    Contains Vancouver/98662 reference")
            # Print first 500 chars of text
            print(f"    Text preview: {text[:500]}")
            break
    except Exception as e:
        print(f"  {url} -> Error: {str(e)[:100]}")

# Try Google search
print('\n=== Trying Google Search ===')
try:
    q = urllib.parse.quote("Let's Remodel bathroom contractor Vancouver WA 98662")
    url = f'https://www.google.com/search?q={q}'
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Extract search results
    for div in soup.select('div.g, div[data-sokoban-container]')[:5]:
        a = div.select_one('a[href]')
        title = div.select_one('h3')
        snippet = div.select_one('div.VwiC3b, span.aCOpRe')
        if a and title:
            print(f"  Title: {title.get_text(strip=True)}")
            print(f"  URL: {a.get('href', 'N/A')}")
            if snippet:
                print(f"  Snippet: {snippet.get_text(strip=True)[:200]}")
            print()
except Exception as e:
    print(f"  Google Error: {e}")

# Try Bing search
print('\n=== Trying Bing Search ===')
try:
    q = urllib.parse.quote("Let's Remodel bathroom contractor Vancouver WA")
    url = f'https://www.bing.com/search?q={q}'
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for li in soup.select('li.b_algo')[:5]:
        a = li.select_one('a')
        snippet = li.select_one('p, .b_caption p')
        if a:
            print(f"  Title: {a.get_text(strip=True)}")
            print(f"  URL: {a.get('href', 'N/A')}")
            if snippet:
                print(f"  Snippet: {snippet.get_text(strip=True)[:200]}")
            print()
except Exception as e:
    print(f"  Bing Error: {e}")
