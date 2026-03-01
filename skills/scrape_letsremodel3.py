import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

def extract_text(html):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Get main page and find rating platform context
html = fetch('https://www.letsremodel.net')
if not html.startswith('ERROR'):
    # Look for image alt text or links near ratings to identify platforms
    # Search for platform names in the HTML
    platforms = re.findall(r'(google|yelp|houzz|bbb|angi|angieslist|homeadvisor|facebook|nextdoor|thumbtack)', html, re.I)
    print('Platforms mentioned in HTML:', list(set(p.lower() for p in platforms)))
    
    # Look for alt text on rating images
    alt_texts = re.findall(r'alt=["\']([^"\']*(?:rating|review|star|google|yelp|houzz|bbb)[^"\']*)["\']', html, re.I)
    print('Alt texts with rating/review:', alt_texts)
    
    # Look for links to review platforms
    review_links = re.findall(r'href=["\']([^"\']*(?:google|yelp|houzz|bbb|angi)[^"\']*)["\']', html, re.I)
    print('Review platform links:', review_links)
    
    # Get the full text and find the ratings section more broadly
    text = extract_text(html)
    
    # Find all occurrences of 'Rated' and get surrounding context
    for m in re.finditer(r'Rated', text):
        start = max(0, m.start() - 150)
        end = min(len(text), m.end() + 200)
        snippet = text[start:end]
        print(f'\n--- Rating context at pos {m.start()} ---')
        print(snippet)
        print('---')

# Also get the about page full text
html2 = fetch('https://www.letsremodel.net/about/')
if not html2.startswith('ERROR'):
    text2 = extract_text(html2)
    # Get the main content after 'About Us'
    idx = text2.find('About Us')
    if idx > -1:
        about_content = text2[idx:idx+2000]
        print('\n=== FULL ABOUT CONTENT ===')
        print(about_content)
