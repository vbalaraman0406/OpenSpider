import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Houzz profile
houzz_url = 'https://www.houzz.com/professionals/general-contractors/mountainwood-pfvwus-pf~1'
print('=== HOUZZ PROFILE ===')
try:
    r = requests.get(houzz_url, headers=headers, timeout=15, allow_redirects=True)
    print(f'Status: {r.status_code}')
    print(f'Final URL: {r.url}')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        # Extract title
        title = soup.find('title')
        print(f'Title: {title.text.strip() if title else "N/A"}')
        # Look for business name, phone, location, rating
        # Try meta tags
        for meta in soup.find_all('meta', attrs={'property': True}):
            prop = meta.get('property', '')
            if any(k in prop.lower() for k in ['title', 'description', 'phone', 'rating']):
                print(f'  {prop}: {meta.get("content", "")[:200]}')
        # Look for phone numbers in text
        text = soup.get_text(' ', strip=True)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phones:
            print(f'Phone numbers found: {phones[:5]}')
        # Look for rating
        rating_match = re.findall(r'(\d+\.?\d*)\s*(?:out of|/)\s*5|rating[:\s]*(\d+\.?\d*)', text.lower())
        if rating_match:
            print(f'Rating matches: {rating_match[:5]}')
        # Look for reviews count
        review_match = re.findall(r'(\d+)\s*reviews?', text.lower())
        if review_match:
            print(f'Review count matches: {review_match[:5]}')
        # Extract key sections - look for specific data
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            print(f'  Heading: {tag.text.strip()[:100]}')
        # Look for structured data
        for script in soup.find_all('script', type='application/ld+json'):
            print(f'  LD+JSON: {script.string[:500] if script.string else "empty"}')
except Exception as e:
    print(f'Error: {e}')

print()

# HomeAdvisor
ha_url = 'https://www.homeadvisor.com/rated.Mountainwood.html'
print('=== HOMEADVISOR PROFILE ===')
try:
    r = requests.get(ha_url, headers=headers, timeout=15, allow_redirects=True)
    print(f'Status: {r.status_code}')
    print(f'Final URL: {r.url}')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.find('title')
        print(f'Title: {title.text.strip() if title else "N/A"}')
        text = soup.get_text(' ', strip=True)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phones:
            print(f'Phone numbers found: {phones[:5]}')
        # Extract key info - first 1000 chars of text
        # Look for location, services
        for kw in ['Vancouver', 'WA', '98662', 'bathroom', 'remodel', 'rating', 'review']:
            idx = text.lower().find(kw.lower())
            if idx >= 0:
                print(f'  Context around "{kw}": ...{text[max(0,idx-50):idx+100]}...')
        for script in soup.find_all('script', type='application/ld+json'):
            print(f'  LD+JSON: {script.string[:500] if script.string else "empty"}')
except Exception as e:
    print(f'Error: {e}')
