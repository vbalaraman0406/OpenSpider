import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'Error: {e}'

# Try common domain patterns
domains = [
    'https://www.letsremodel.com',
    'https://letsremodel.com',
    'https://www.letsremodel.net',
    'https://letsremodel.net',
    'https://www.letsremodelwa.com',
]

for domain in domains:
    print(f'\n=== Trying {domain} ===')
    html = fetch_url(domain)
    if 'Error' in html[:50]:
        print(html[:200])
    else:
        # Extract title
        title = re.findall(r'<title>(.*?)</title>', html, re.IGNORECASE)
        print(f'Title: {title[0] if title else "N/A"}')
        
        # Extract phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        print(f'Phones: {list(set(phones))}')
        
        # Check if Vancouver WA is mentioned
        if 'vancouver' in html.lower() or 'Vancouver' in html:
            print('Vancouver mentioned: YES')
        else:
            print('Vancouver mentioned: NO')
        
        # Extract meta description
        meta = re.findall(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]+)', html, re.IGNORECASE)
        print(f'Meta desc: {meta[0][:200] if meta else "N/A"}')
        
        print(f'HTML length: {len(html)}')

# Try Yelp search
print('\n=== YELP SEARCH ===')
yelp_url = "https://www.yelp.com/search?find_desc=Let%27s+Remodel&find_loc=Vancouver%2C+WA"
html_yelp = fetch_url(yelp_url)
if 'Error' not in html_yelp[:50]:
    # Look for business listings
    biz_links = re.findall(r'href="(/biz/[^"]+)"', html_yelp)
    for b in list(set(biz_links))[:10]:
        print(f'Yelp biz: https://www.yelp.com{b}')
    
    # Look for ratings
    ratings = re.findall(r'(\d+\.?\d*)\s*(?:star|rating)', html_yelp, re.IGNORECASE)
    print(f'Ratings found: {ratings[:5]}')
    
    # Look for review counts
    reviews = re.findall(r'(\d+)\s*review', html_yelp, re.IGNORECASE)
    print(f'Review counts: {reviews[:5]}')
else:
    print(html_yelp[:200])

# Try BBB
print('\n=== BBB SEARCH ===')
bbb_url = "https://www.bbb.org/search?find_country=US&find_entity=10126-000&find_text=Let%27s+Remodel&find_loc=Vancouver%2C+WA&page=1"
html_bbb = fetch_url(bbb_url)
if 'Error' not in html_bbb[:50]:
    print(f'BBB HTML length: {len(html_bbb)}')
    bbb_links = re.findall(r'href="([^"]*lets-remodel[^"]*|[^"]*let-s-remodel[^"]*|[^"]*letsremodel[^"]*)', html_bbb, re.IGNORECASE)
    print(f'BBB links: {bbb_links[:5]}')
else:
    print(html_bbb[:200])
