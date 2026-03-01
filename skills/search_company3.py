import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Deep dive into letsremodel.com
print('=== Deep dive: letsremodel.com ===')
try:
    resp = requests.get('https://www.letsremodel.com', headers=headers, timeout=15)
    html = resp.text
    print(f'HTML length: {len(html)}')
    print(f'First 2000 chars of HTML:')
    print(html[:2000])
    print('\n--- Searching for phone numbers ---')
    phones = re.findall(r'[\(]?\d{3}[\)]?[\s\-\.]?\d{3}[\s\-\.]?\d{4}', html)
    print(f'Phones: {list(set(phones))}')
    print('--- Searching for email ---')
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
    print(f'Emails: {list(set(emails))}')
    # Check for JavaScript redirect or SPA
    if 'react' in html.lower() or 'angular' in html.lower() or 'vue' in html.lower():
        print('Likely a SPA (Single Page App)')
    scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
    print(f'Script sources: {scripts[:5]}')
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    print(f'Links: {links[:10]}')
except Exception as e:
    print(f'Error: {e}')

# Try Yelp search
print('\n=== Yelp Search ===')
try:
    url = 'https://www.yelp.com/search?find_desc=Let%27s+Remodel&find_loc=Vancouver%2C+WA+98662'
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Look for business cards
    for a in soup.select('a[href*="/biz/"]')[:10]:
        name = a.get_text(strip=True)
        href = a.get('href', '')
        if name and len(name) > 3 and 'remodel' in name.lower():
            print(f'  Name: {name}')
            print(f'  URL: https://www.yelp.com{href}')
except Exception as e:
    print(f'Yelp Error: {e}')

# Try BBB
print('\n=== BBB Search ===')
try:
    url = 'https://www.bbb.org/search?find_country=US&find_loc=Vancouver%2C%20WA&find_text=Let%27s%20Remodel&find_type=Category&page=1'
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(' ', strip=True)[:1000]
    print(f'BBB text: {text[:500]}')
except Exception as e:
    print(f'BBB Error: {e}')

# Try subpages of letsremodel.com
print('\n=== Trying subpages ===')
for path in ['/about', '/contact', '/services', '/bathroom-remodeling', '/about-us', '/contact-us']:
    try:
        resp = requests.get(f'https://www.letsremodel.com{path}', headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = soup.get_text(' ', strip=True)[:300]
            print(f'  {path} -> {resp.status_code}: {text[:200]}')
    except:
        pass
