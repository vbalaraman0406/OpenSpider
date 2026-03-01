import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# First, get the BBB search results page
url = 'https://www.bbb.org/search?find_country=US&find_loc=Vancouver%2C%20WA&find_text=Fazzolari&find_type=Category&page=1'
resp = requests.get(url, headers=headers, timeout=15)
print(f'BBB Search Status: {resp.status_code}')

soup = BeautifulSoup(resp.text, 'html.parser')

# Find all links that might be business profile links
links = soup.find_all('a', href=True)
fazz_links = []
for link in links:
    href = link['href']
    text = link.get_text(strip=True)
    if 'fazzolari' in href.lower() or 'fazzolari' in text.lower():
        fazz_links.append((text, href))
        print(f'  Link: {text} -> {href}')

# Also search for any text containing fazzolari
all_text = soup.get_text()
idx = all_text.lower().find('fazzolari')
if idx >= 0:
    context = all_text[max(0,idx-200):idx+500]
    print(f'\n=== BBB Context around Fazzolari ===')
    print(context.strip())

# Try to find result cards
result_cards = soup.find_all('div', class_=lambda c: c and 'result' in c.lower()) if soup else []
print(f'\nResult cards found: {len(result_cards)}')
for card in result_cards[:3]:
    print(card.get_text(separator=' | ', strip=True)[:500])
    card_links = card.find_all('a', href=True)
    for cl in card_links:
        print(f'  Card link: {cl["href"]}')
