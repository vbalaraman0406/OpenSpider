import urllib.request
import re

urls = {
    'Reliable Men': [
        'https://www.reliablemen.com',
        'https://reliablemen.com'
    ],
    'Lets Remodel': [
        'https://www.letsremodel.com',
        'https://letsremodel.com'
    ],
    'Fazzolari': [
        'https://www.fazzolari.com',
        'https://fazzolaricustomhomes.com',
        'https://www.fazzolaricustomhomes.com'
    ],
    'Mountainwood': [
        'https://www.mountainwoodhomes.com',
        'https://mountainwoodhomes.com',
        'https://www.mountainwood.com'
    ],
    'Beto and Son': [
        'https://www.betoandson.com',
        'https://betoandson.com',
        'https://www.betoandsonconstruction.com'
    ]
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for name, url_list in urls.items():
    print(f'\n=== {name} ===')
    for url in url_list:
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=8)
            html = resp.read().decode('utf-8', errors='ignore')[:3000]
            # Extract title
            title = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
            title_text = title.group(1).strip() if title else 'No title'
            # Extract phone numbers
            phones = re.findall(r'[\(]?\d{3}[\)]?[\s.-]?\d{3}[\s.-]?\d{4}', html)
            # Extract meta description
            desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.I)
            desc_text = desc.group(1).strip() if desc else 'No description'
            print(f'  URL: {url}')
            print(f'  Title: {title_text}')
            print(f'  Description: {desc_text[:200]}')
            print(f'  Phones: {phones[:3]}')
            print(f'  Status: OK')
            break
        except Exception as e:
            print(f'  {url} -> Error: {str(e)[:80]}')
