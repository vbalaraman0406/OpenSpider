import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# 1. Try Bing and dump a portion of raw HTML to understand structure
url = 'https://www.bing.com/search?q=%22Reliable+Men%22+bathroom+remodel+Vancouver+WA'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Check if we got a CAPTCHA or block
    if 'captcha' in html.lower() or 'unusual traffic' in html.lower():
        print('BING: Blocked by CAPTCHA')
    else:
        # Try different result patterns
        # Pattern 1: b_algo
        p1 = re.findall(r'class="b_algo"', html)
        print(f'BING b_algo count: {len(p1)}')
        
        # Pattern 2: any href with title
        links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html)
        print(f'BING total links: {len(links)}')
        for l in links[:15]:
            title = re.sub(r'<[^>]+>', '', l[1]).strip()
            if title and len(title) > 5 and 'bing' not in l[0].lower() and 'microsoft' not in l[0].lower():
                print(f'  Link: {l[0][:120]}')
                print(f'  Title: {title[:100]}')
                print()
        
        # Print a chunk of the body to see structure
        body = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if body:
            text = re.sub(r'<[^>]+>', ' ', body.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            print(f'\nBING body text (first 1500 chars):')
            print(text[:1500])
except Exception as e:
    print(f'BING Error: {e}')

# 2. Try Google Places text search via scraping
print('\n\n=== TRYING GOOGLE MAPS ===' )
url2 = 'https://www.google.com/maps/search/Reliable+Men+bathroom+remodel+Vancouver+WA+98662'
try:
    req = urllib.request.Request(url2, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html2 = resp.read().decode('utf-8', errors='ignore')
    text2 = re.sub(r'<[^>]+>', ' ', html2)
    text2 = re.sub(r'\s+', ' ', text2).strip()
    # Look for phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text2)
    print(f'Google Maps phones found: {phones[:5]}')
    print(f'Google Maps text (first 1000 chars): {text2[:1000]}')
except Exception as e:
    print(f'Google Maps Error: {e}')

# 3. Try searching on Thumbtack
print('\n\n=== TRYING THUMBTACK ===')
url3 = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
try:
    req = urllib.request.Request(url3, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html3 = resp.read().decode('utf-8', errors='ignore')
    text3 = re.sub(r'<[^>]+>', ' ', html3)
    text3 = re.sub(r'\s+', ' ', text3).strip()
    if 'reliable men' in text3.lower():
        idx = text3.lower().index('reliable men')
        print(f'Found on Thumbtack! Context: {text3[max(0,idx-100):idx+300]}')
    else:
        print('Not found on Thumbtack')
except Exception as e:
    print(f'Thumbtack Error: {e}')
