import urllib.request
import re
import html as htmlmod

def fetch_full(url, max_chars=5000):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8', errors='replace')
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<br[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

# Get the full Vancouver residential permits page
url = 'https://www.cityofvancouver.us/permits/residential-building-permits/'
content = fetch_full(url, 8000)

# Find sections about when permits are required/not required
lines = content.split('\n')
relevant = []
keywords = ['permit', 'required', 'not required', 'exempt', 'plumb', 'tile', 'bathroom', 'remodel', 'vanity', 'cosmetic', 'flooring', 'fixture', 'faucet', 'sink', 'replace', 'like for like', 'like-for-like', 'mechanical', 'valve']
for i, line in enumerate(lines):
    low = line.lower()
    if any(k in low for k in keywords):
        # include surrounding context
        start = max(0, i-1)
        end = min(len(lines), i+2)
        for j in range(start, end):
            if lines[j].strip() and lines[j].strip() not in relevant:
                relevant.append(lines[j].strip())

print('RELEVANT SECTIONS FROM VANCOUVER PERMITS PAGE:')
print('='*60)
for r in relevant[:40]:
    print(r)

# Also try the specific FAQ or exemption page
print('\n\n')
print('='*60)
print('TRYING VANCOUVER PERMIT EXEMPTIONS...')
print('='*60)
try:
    url2 = 'https://www.cityofvancouver.us/permits/do-i-need-a-permit/'
    content2 = fetch_full(url2, 8000)
    lines2 = content2.split('\n')
    relevant2 = []
    for i, line in enumerate(lines2):
        low = line.lower()
        if any(k in low for k in keywords):
            start = max(0, i-1)
            end = min(len(lines2), i+2)
            for j in range(start, end):
                if lines2[j].strip() and lines2[j].strip() not in relevant2:
                    relevant2.append(lines2[j].strip())
    for r in relevant2[:40]:
        print(r)
    if not relevant2:
        print(content2[:2000])
except Exception as e:
    print(f'Error: {e}')
