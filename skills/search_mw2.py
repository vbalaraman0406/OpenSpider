import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try multiple possible website URLs
urls_to_try = [
    'https://www.mountainwoodconstruction.com',
    'https://www.mountainwoodcontractor.com',
    'https://www.mountainwoodbuilders.com',
    'https://www.mountainwoodremodeling.com',
    'https://mountainwoodconstruction.com',
    'https://mountainwoodcontractor.com',
    'https://mountainwoodbuilders.com',
    'https://mountainwoodremodeling.com',
    'https://mountainwoodhomes.com',
    'https://www.mountainwoodhomes.com',
]

print('=== TRYING DIRECT URLS ===')
for url in urls_to_try:
    try:
        resp = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else 'No title'
            print(f'FOUND: {url} -> {resp.url}')
            print(f'  Title: {title}')
            # Look for phone numbers
            import re
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resp.text)
            if phones:
                print(f'  Phones: {list(set(phones))[:5]}')
            print()
    except Exception as e:
        pass

# Search Yelp
print('\n=== YELP SEARCH ===')
try:
    yelp_url = 'https://www.yelp.com/search?find_desc=Mountainwood&find_loc=Vancouver%2C+WA'
    resp = requests.get(yelp_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Look for business links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if 'mountainwood' in text.lower() or 'mountainwood' in href.lower():
            print(f'Yelp result: {text} -> {href}')
except Exception as e:
    print(f'Yelp error: {e}')

# Search BBB
print('\n=== BBB SEARCH ===')
try:
    bbb_url = 'https://www.bbb.org/search?find_country=US&find_entity=10236-000&find_text=Mountainwood&find_loc=Vancouver%2C+WA&page=1'
    resp = requests.get(bbb_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if 'mountainwood' in text.lower() or 'mountainwood' in href.lower():
            print(f'BBB result: {text} -> {href}')
except Exception as e:
    print(f'BBB error: {e}')

# Try Google search via different approach
print('\n=== ADDITIONAL SEARCH ===')
try:
    query = 'site:yelp.com+Mountainwood+Vancouver+WA'
    ddg = f'https://html.duckduckgo.com/html/?q={query}'
    resp = requests.get(ddg, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = soup.select('.result__a')
    for r in results[:5]:
        title = r.get_text(strip=True)
        print(f'  {title}')
except Exception as e:
    print(f'Error: {e}')
