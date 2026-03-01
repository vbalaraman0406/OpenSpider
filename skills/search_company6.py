import urllib.request
import urllib.parse
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Yelp search
try:
    url = 'https://www.yelp.com/search?find_desc=' + urllib.parse.quote("Let's Remodel") + '&find_loc=' + urllib.parse.quote('Vancouver, WA 98662')
    print(f'Yelp URL: {url}')
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract business cards
    biz_matches = re.findall(r'"name":"([^"]*remodel[^"]*)"|class="css-[^"]*"[^>]*>([^<]*[Rr]emodel[^<]*)<', html, re.IGNORECASE)
    print(f'Yelp matches: {biz_matches[:10]}')
    # Look for phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
    print(f'Yelp phones: {phones[:5]}')
    # Look for ratings
    ratings = re.findall(r'(\d+\.\d+)\s*star', html, re.IGNORECASE)
    print(f'Yelp ratings: {ratings[:5]}')
    # Check for Let's Remodel specifically
    if "let's remodel" in html.lower() or 'lets remodel' in html.lower():
        print('FOUND on Yelp!')
        idx = html.lower().find('let')
        print(html[max(0,idx-200):idx+500])
    else:
        print('Not found on Yelp')
except Exception as e:
    print(f'Yelp error: {e}')

# Try Thumbtack
try:
    url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    if "let's remodel" in html.lower() or 'lets remodel' in html.lower():
        print('FOUND on Thumbtack!')
        idx = html.lower().find('let')
        print(html[max(0,idx-200):idx+500])
    else:
        print('Not found on Thumbtack')
except Exception as e:
    print(f'Thumbtack error: {e}')

# Try HomeAdvisor / Angi
try:
    url = 'https://www.angi.com/companylist/vancouver/bathroom-remodel.htm'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    if "let's remodel" in html.lower() or 'lets remodel' in html.lower():
        print('FOUND on Angi!')
        idx = html.lower().find('let')
        print(html[max(0,idx-200):idx+500])
    else:
        print('Not found on Angi')
except Exception as e:
    print(f'Angi error: {e}')

# Try searching Bing with different query
try:
    query = urllib.parse.quote('"Let\'s Remodel" bathroom Vancouver WA phone')
    url = f'https://www.bing.com/search?q={query}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract snippets
    snippets = re.findall(r'<p[^>]*>([^<]*(?:[Rr]emodel|Vancouver)[^<]*)</p>', html)
    print(f'Bing snippets: {snippets[:5]}')
    links = re.findall(r'<a[^>]*href="(https?://[^"]*remodel[^"]*)"', html, re.IGNORECASE)
    print(f'Bing remodel links: {links[:10]}')
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
    print(f'Bing phones: {phones[:5]}')
except Exception as e:
    print(f'Bing error: {e}')

print('\nDone with search round 6')
