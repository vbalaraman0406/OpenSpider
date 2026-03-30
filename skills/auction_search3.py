import requests
import re
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Search Google for each auction site + Vancouver WA 5 bedroom
sites = [
    ('Auction.com', 'site:auction.com Vancouver WA 5 bedroom house under 600000'),
    ('Hubzu.com', 'site:hubzu.com Vancouver WA 5 bedroom'),
    ('Xome.com', 'site:xome.com Vancouver WA 5 bedroom'),
    ('HUDHomeStore.gov', 'site:hudhomestore.gov Vancouver WA 5 bedroom'),
    ('Foreclosure.com', 'site:foreclosure.com Vancouver WA 5 bedroom'),
]

for site_name, query in sites:
    print(f"\n=== {site_name} ===")
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num=10'
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all('div', class_='g')
        if not results:
            links = soup.find_all('a', href=True)
            site_key = site_name.lower().split('.')[0]
            relevant = [l for l in links if site_key in l['href'].lower()]
            if relevant:
                for l in relevant[:5]:
                    print(f"Link: {l['href']}")
                    print(f"Text: {l.get_text()[:200]}")
            else:
                if 'captcha' in r.text.lower() or 'unusual traffic' in r.text.lower():
                    print("Google CAPTCHA detected")
                else:
                    title_tag = soup.find('title')
                    print(f"No results. Title: {title_tag.string if title_tag else 'N/A'}")
                    print(f"Text sample: {soup.get_text()[:300]}")
        else:
            for result in results[:5]:
                title = result.find('h3')
                link = result.find('a', href=True)
                print(f"Title: {title.get_text() if title else 'N/A'}")
                print(f"Link: {link['href'] if link else 'N/A'}")
                print(f"Snippet: {result.get_text()[:200]}")
                print('---')
    except Exception as e:
        print(f"Error: {e}")

# Try HUD Home Store directly
print("\n=== HUD HOME STORE DIRECT ===")
try:
    url = 'https://www.hudhomestore.gov/Listing/PropertySearchResult'
    data = {
        'sState': 'WA',
        'sCity': 'VANCOUVER',
        'sBedrooms': '5',
        'sMaxPrice': '600000',
        'sPropertyType': 'SFR'
    }
    r = requests.post(url, headers=headers, data=data, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    listings = soup.find_all('div', class_='property')
    if not listings:
        listings = soup.find_all('div', class_='listing')
    if not listings:
        listings = soup.find_all('tr')
    if listings:
        for l in listings[:10]:
            text = l.get_text().strip()
            if text and len(text) > 10:
                print(text[:300])
                print('---')
    else:
        text = soup.get_text()
        addresses = re.findall(r'\d+\s+\w+.*(?:St|Ave|Dr|Rd|Blvd|Ct|Ln|Way|Pl)', text)
        if addresses:
            for a in addresses[:10]:
                print(f"Address: {a}")
        else:
            print(f"Page text: {text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Also try broader Google searches for foreclosure/auction homes in Vancouver WA
print("\n=== GOOGLE BROADER SEARCH ===")
try:
    query = 'foreclosure auction 5 bedroom house Vancouver WA under 600000 2024 2025'
    url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num=10'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('div', class_='g')
    if results:
        for result in results[:5]:
            title = result.find('h3')
            link = result.find('a', href=True)
            print(f"Title: {title.get_text() if title else 'N/A'}")
            print(f"Link: {link['href'] if link else 'N/A'}")
            print(f"Snippet: {result.get_text()[:200]}")
            print('---')
    else:
        print(f"No results found. Text: {soup.get_text()[:300]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== COMPLETE ===")
