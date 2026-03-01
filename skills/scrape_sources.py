import requests
from bs4 import BeautifulSoup
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try HomeGuide
print('=== HomeGuide ===')
try:
    r = requests.get('https://homeguide.com/wa/vancouver/bathroom-remodeling/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for contractor cards
    cards = soup.find_all(['div','li'], class_=re.compile(r'(provider|pro-card|listing|result)', re.I))
    print(f'Found {len(cards)} cards')
    # Try to find names and ratings
    names = soup.find_all(string=re.compile(r'(LLC|Inc|Remodel|Construction|Tile|Bath)', re.I))
    for n in names[:20]:
        print(f'  Name match: {n.strip()[:80]}')
    # Look for JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    for s in scripts:
        try:
            data = json.loads(s.string)
            print(f'JSON-LD type: {data.get("@type", "unknown")}')
            if isinstance(data, list):
                for item in data[:5]:
                    print(f'  - {item.get("name","?")} rating={item.get("aggregateRating",{}).get("ratingValue","?")}')
            elif data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', [])[:10]:
                    i = item.get('item', {})
                    print(f'  - {i.get("name","?")} rating={i.get("aggregateRating",{}).get("ratingValue","?")}')
        except: pass
except Exception as e:
    print(f'HomeGuide error: {e}')

print()
print('=== Thumbtack ===')
try:
    r = requests.get('https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    for s in scripts:
        try:
            data = json.loads(s.string)
            if isinstance(data, list):
                for item in data[:15]:
                    name = item.get('name', '?')
                    rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                    reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                    phone = item.get('telephone', 'N/A')
                    print(f'  {name} | Rating: {rating} | Reviews: {reviews} | Phone: {phone}')
            elif data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                name = data.get('name', '?')
                rating = data.get('aggregateRating', {}).get('ratingValue', 'N/A')
                reviews = data.get('aggregateRating', {}).get('reviewCount', 'N/A')
                print(f'  {name} | Rating: {rating} | Reviews: {reviews}')
        except: pass
except Exception as e:
    print(f'Thumbtack error: {e}')

print()
print('=== Yellow Pages ===')
try:
    r = requests.get('https://www.yellowpages.com/vancouver-wa/bathroom-remodeling', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('div', class_=re.compile(r'result', re.I))[:10]
    print(f'Found {len(results)} results')
    for res in results:
        name_tag = res.find(['a','h2'], class_=re.compile(r'(name|business)', re.I))
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'
        phone_tag = res.find('div', class_=re.compile(r'phone', re.I))
        phone = phone_tag.get_text(strip=True) if phone_tag else 'N/A'
        print(f'  {name} | Phone: {phone}')
except Exception as e:
    print(f'YP error: {e}')
