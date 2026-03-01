import urllib.request
import urllib.parse
import re

def fetch_page(url, label):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', html_clean)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        return f'Error: {e}'

# 1. Try Alignable page
print('=== ALIGNABLE ===')
url1 = 'https://www.alignable.com/vancouver-wa/reliable-men-construction-llc'
text1 = fetch_page(url1, 'Alignable')
# Extract relevant portions
for keyword in ['bathroom', 'remodel', 'service', 'rating', 'review', 'phone', 'website', 'reliable men', 'construction', 'speciali']:
    idx = text1.lower().find(keyword)
    if idx >= 0:
        snippet = text1[max(0,idx-50):idx+200]
        print(f'[{keyword}]: {snippet}')
print()

# 2. Try BBB search
print('=== BBB ===')
url2 = 'https://www.bbb.org/search?find_country=US&find_text=Reliable+Men+Construction&find_loc=Vancouver+WA'
text2 = fetch_page(url2, 'BBB')
for keyword in ['reliable men', 'rating', 'review', 'phone', 'website', 'bathroom']:
    idx = text2.lower().find(keyword)
    if idx >= 0:
        snippet = text2[max(0,idx-30):idx+200]
        print(f'[{keyword}]: {snippet}')
print()

# 3. Try DuckDuckGo for more specific info
print('=== DDG DETAILED ===')
ddg_url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote('Reliable Men Construction LLC Vancouver WA 98662 phone rating reviews services bathroom remodel')
text3 = fetch_page(ddg_url, 'DDG detailed')
# Extract result snippets
result_parts = re.split(r'(?:result__|result--)', text3)
for i, part in enumerate(result_parts[:8]):
    # Get first 300 chars of each result
    clean = part.strip()[:300]
    if 'reliable' in clean.lower() or 'bathroom' in clean.lower() or 'remodel' in clean.lower():
        print(f'Result {i}: {clean}')
        print('---')

# 4. Try Google Maps / Places alternative
print('\n=== MANTA ===')
url4 = 'https://www.manta.com/c/m1wrqhx/reliable-men-construction-llc'
text4 = fetch_page(url4, 'Manta')
for keyword in ['phone', 'service', 'rating', 'review', 'bathroom', 'remodel', 'website', 'reliable men']:
    idx = text4.lower().find(keyword)
    if idx >= 0:
        snippet = text4[max(0,idx-30):idx+200]
        print(f'[{keyword}]: {snippet}')
