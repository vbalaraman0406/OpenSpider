import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# 1. Try WA Secretary of State business search
print('=== WA Secretary of State ===' )
sos_url = 'https://ccfs.sos.wa.gov/api/BusinessSearch?BusinessName=lets+remodel&SearchType=Contains'
try:
    req = urllib.request.Request(sos_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read().decode('utf-8', errors='ignore')
        # Try to parse as JSON
        try:
            results = json.loads(data)
            for r in results[:5]:
                print(json.dumps(r, indent=2))
        except:
            print(data[:1000])
except Exception as e:
    print(f'SOS error: {e}')

# 2. Try WA L&I contractor license search
print('\n=== WA L&I Contractor Search ===')
lni_url = 'https://fortress.wa.gov/lni/bbip/Search.aspx'
try:
    # First try a direct API-style search
    search_url = f'https://fortress.wa.gov/lni/bbip/Results.aspx?BusinessName=lets+remodel&City=Vancouver&County=&Ession=&Zip=98662'
    html = fetch(search_url)
    # Look for business names and license numbers
    names = re.findall(r'BusinessName[^>]*>([^<]+)', html)
    licenses = re.findall(r'[A-Z]{5,}\*?\d{3}[A-Z]{2}', html)
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
    print(f'Names found: {names[:5]}')
    print(f'Licenses: {licenses[:5]}')
    print(f'Phones: {phones[:5]}')
    if not names and not licenses:
        print(html[:800])
except Exception as e:
    print(f'L&I error: {e}')

# 3. Try Google with different query
print('\n=== Google Search ===')
query = urllib.parse.quote('"Let\'s Remodel" Vancouver WA bathroom contractor')
google_url = f'https://www.google.com/search?q={query}'
html = fetch(google_url)
if 'ERROR' not in html:
    # Extract snippets
    snippets = re.findall(r'<span[^>]*>([^<]{30,200})</span>', html)
    for s in snippets[:10]:
        if 'remodel' in s.lower() or 'vancouver' in s.lower() or 'bathroom' in s.lower():
            print(s)
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
    print(f'Phones: {phones[:5]}')
    links = re.findall(r'href="(https?://[^"]+remodel[^"]+)"', html, re.I)
    print(f'Links: {links[:5]}')
else:
    print(html[:500])

# 4. Try Facebook search
print('\n=== Facebook Search ===')
fb_url = f'https://www.facebook.com/search/pages/?q={urllib.parse.quote("Let s Remodel Vancouver WA")}'
html = fetch(fb_url)
if 'ERROR' not in html:
    titles = re.findall(r'<title>([^<]+)</title>', html)
    print(f'Title: {titles}')
    print(html[:500])
else:
    print(html[:300])

print('\nDone with search round 7')