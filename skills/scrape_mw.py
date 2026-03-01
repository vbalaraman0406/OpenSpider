import requests
from bs4 import BeautifulSoup
import json, re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. Mountainwood Homes main site
try:
    r = requests.get('https://www.mountainwoodhomes.com/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.string if soup.title else 'N/A'
    # Look for phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', r.text)
    phones = list(set(phones))
    # Look for address
    print(f'=== MAIN SITE ===')
    print(f'Title: {title}')
    print(f'Phones found: {phones[:5]}')
    # Get meta description
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta:
        print(f'Description: {meta.get("content", "")[:300]}')
    # Look for services/bathroom mentions
    text = soup.get_text(' ', strip=True)[:2000]
    bath_mentions = [s.strip() for s in text.split('.') if 'bath' in s.lower() or 'tile' in s.lower() or 'vanity' in s.lower()][:5]
    print(f'Bath/tile mentions: {bath_mentions}')
except Exception as e:
    print(f'Main site error: {e}')

print()

# 2. BuildZoom page
try:
    r = requests.get('https://www.buildzoom.com/contractor/mountainwood-homes-inc-wa', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)
    # Extract rating, reviews, license info
    score_match = re.search(r'BuildZoom score[:\s]*(\d+)', text, re.I)
    rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of|/)\s*5', text, re.I)
    review_match = re.search(r'(\d+)\s*review', text, re.I)
    license_match = re.search(r'license[^.]{0,200}', text, re.I)
    print(f'=== BUILDZOOM ===')
    print(f'BZ Score: {score_match.group(1) if score_match else "N/A"}')
    print(f'Rating: {rating_match.group(0) if rating_match else "N/A"}')
    print(f'Reviews: {review_match.group(0) if review_match else "N/A"}')
    print(f'License: {license_match.group(0)[:200] if license_match else "N/A"}')
    phones_bz = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', r.text)
    print(f'Phones: {list(set(phones_bz))[:3]}')
except Exception as e:
    print(f'BuildZoom error: {e}')

print()

# 3. YellowPages
try:
    r = requests.get('https://www.yellowpages.com/vancouver-wa/mountainwood-homes-inc', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Find business listings
    listings = soup.find_all('div', class_='result')
    print(f'=== YELLOWPAGES ===')
    print(f'Listings found: {len(listings)}')
    for li in listings[:3]:
        name = li.find('a', class_='business-name')
        phone = li.find('div', class_='phones')
        rating = li.find('div', class_='ratings')
        print(f'  Name: {name.get_text(strip=True) if name else "N/A"}')
        print(f'  Phone: {phone.get_text(strip=True) if phone else "N/A"}')
        print(f'  Rating: {rating.get_text(strip=True)[:100] if rating else "N/A"}')
except Exception as e:
    print(f'YellowPages error: {e}')

print()

# 4. Service areas page for bathroom details
try:
    r = requests.get('https://www.mountainwoodhomes.com/service-areas/southwest-washington/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)
    bath_sentences = [s.strip() for s in text.split('.') if any(w in s.lower() for w in ['bath','tile','vanity','floor','remodel'])][:8]
    print(f'=== SERVICE PAGE ===')
    for s in bath_sentences:
        print(f'  - {s[:200]}')
except Exception as e:
    print(f'Service page error: {e}')
