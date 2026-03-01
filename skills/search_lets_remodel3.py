import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

def extract_text(html):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def find_phones(text):
    return list(set(re.findall(r'\(?\d{3}\)?[\-\.\s]?\d{3}[\-\.\s]\d{4}', text)))

# Try Bing
print('=== BING SEARCH ===')
html = fetch('https://www.bing.com/search?q=%22Let%27s+Remodel%22+Vancouver+WA+contractor')
if not html.startswith('ERROR'):
    text = extract_text(html)
    phones = find_phones(text)
    # Extract URLs
    urls = re.findall(r'href="(https?://[^"]+)"', html)
    relevant = [u for u in urls if 'bing.com' not in u and 'microsoft' not in u][:10]
    print('Phones:', phones[:5])
    print('URLs:', relevant[:10])
    print('Text:', text[:1500])
else:
    print(html)

# Try DuckDuckGo HTML
print('\n=== DUCKDUCKGO ===')
html = fetch('https://html.duckduckgo.com/html/?q=%22Let%27s+Remodel%22+Vancouver+WA+contractor+bathroom')
if not html.startswith('ERROR'):
    text = extract_text(html)
    phones = find_phones(text)
    urls = re.findall(r'href="(https?://[^"]+)"', html)
    relevant = [u for u in urls if 'duckduckgo' not in u][:10]
    print('Phones:', phones[:5])
    print('URLs:', relevant[:10])
    print('Text:', text[:1500])
else:
    print(html)

# Try direct URL variations
print('\n=== DIRECT URLS ===')
for url in ['https://www.letsremodel.com', 'https://letsremodel.com', 'https://www.letsremodel.net', 'https://www.letsremodelllc.com', 'https://www.letsremodeling.com']:
    html = fetch(url)
    if not html.startswith('ERROR') and len(html) > 100:
        title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.I|re.DOTALL)
        phones = find_phones(html)
        print(f'{url} -> Title: {title[0].strip()[:100] if title else "none"}, Phones: {phones[:3]}, Length: {len(html)}')
    else:
        print(f'{url} -> {html[:100]}')

# Try Yelp search
print('\n=== YELP ===')
html = fetch('https://www.yelp.com/search?find_desc=Let%27s+Remodel&find_loc=Vancouver%2C+WA')
if not html.startswith('ERROR'):
    text = extract_text(html)
    print('Text:', text[:1000])
else:
    print(html)
