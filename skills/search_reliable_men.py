import urllib.request
import re
import json

# Try multiple sources
urls_to_try = [
    ('Yelp', 'https://www.yelp.com/search?find_desc=Reliable+Men+bathroom+remodel&find_loc=Vancouver%2C+WA+98662'),
    ('YellowPages', 'https://www.yellowpages.com/vancouver-wa/reliable-men'),
    ('BBB', 'https://www.bbb.org/search?find_country=US&find_text=Reliable+Men&find_loc=Vancouver%2C+WA+98662&find_type=Category'),
    ('Bing2', 'https://www.bing.com/search?q=%22Reliable+Men%22+bathroom+remodel+Vancouver+WA'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

for source, url in urls_to_try:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Look for mentions of "Reliable Men"
        matches = [m.start() for m in re.finditer(r'[Rr]eliable\s*[Mm]en', html)]
        print(f'\n=== {source} ===')
        print(f'Status: OK, Length: {len(html)}')
        print(f'Found {len(matches)} mentions of Reliable Men')
        
        if matches:
            for m in matches[:3]:
                start = max(0, m-100)
                end = min(len(html), m+300)
                snippet = html[start:end]
                # Clean HTML tags
                snippet = re.sub(r'<[^>]+>', ' ', snippet)
                snippet = re.sub(r'\s+', ' ', snippet).strip()
                print(f'Context: ...{snippet}...')
        else:
            # Check for any phone numbers or business info
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html[:5000])
            print(f'Phone numbers found in page: {phones[:5]}')
            # Print title
            title = re.findall(r'<title>(.*?)</title>', html)
            print(f'Page title: {title[0][:100] if title else "N/A"}')
    except Exception as e:
        print(f'\n=== {source} ===')
        print(f'Error: {str(e)[:200]}')
