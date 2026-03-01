import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# First, let's see what Google actually returned
query = 'Fazzolari contractor Vancouver WA'
url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num=10'
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Print all links found
print('=== Google Links ===')
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)[:100]
    if '/url?q=' in href or ('http' in href and 'google' not in href):
        print(f'{text} -> {href[:150]}')

# Print all visible text blocks
print('\n=== Google Text Blocks ===')
for tag in soup.find_all(['h3', 'span', 'div']):
    text = tag.get_text(strip=True)
    if len(text) > 30 and len(text) < 300:
        if any(kw in text.lower() for kw in ['fazzolari', 'contractor', 'remodel', 'vancouver', 'bathroom']):
            print(f'  {text[:200]}')

# Try Yelp directly
print('\n=== Yelp Search ===')
yelp_url = 'https://www.yelp.com/search?find_desc=Fazzolari&find_loc=Vancouver%2C+WA+98662'
try:
    resp2 = requests.get(yelp_url, headers=headers, timeout=15)
    print(f'Yelp Status: {resp2.status_code}')
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    for tag in soup2.find_all(['a', 'h3', 'h4', 'span']):
        text = tag.get_text(strip=True)
        if 'fazzolari' in text.lower():
            print(f'  Yelp Found: {text[:200]}')
    # Check if no results
    page_text = soup2.get_text().lower()
    if 'no results' in page_text or 'we could' in page_text:
        print('  Yelp: No results found for Fazzolari')
except Exception as e:
    print(f'Yelp error: {e}')

# Try BBB
print('\n=== BBB Search ===')
bbb_url = 'https://www.bbb.org/search?find_country=US&find_text=Fazzolari&find_loc=Vancouver%2C+WA&find_type=Category'
try:
    resp3 = requests.get(bbb_url, headers=headers, timeout=15)
    print(f'BBB Status: {resp3.status_code}')
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    for tag in soup3.find_all(['a', 'h3', 'h4', 'span', 'p']):
        text = tag.get_text(strip=True)
        if 'fazzolari' in text.lower():
            print(f'  BBB Found: {text[:200]}')
except Exception as e:
    print(f'BBB error: {e}')

# Try searching with 'site:yelp.com' on Bing
print('\n=== Bing site:yelp.com ===')
bing_url = f'https://www.bing.com/search?q={requests.utils.quote("Fazzolari Vancouver WA site:yelp.com")}'
try:
    resp4 = requests.get(bing_url, headers=headers, timeout=15)
    soup4 = BeautifulSoup(resp4.text, 'html.parser')
    for tag in soup4.find_all(['h2', 'a', 'p', 'li']):
        text = tag.get_text(strip=True)
        if 'fazzolari' in text.lower() and len(text) > 10:
            print(f'  {text[:200]}')
    if 'fazzolari' not in resp4.text.lower():
        print('  No Fazzolari results on Bing/Yelp')
except Exception as e:
    print(f'Bing error: {e}')
