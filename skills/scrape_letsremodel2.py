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

# Get about page
html = fetch('https://www.letsremodel.net/about/')
if not html.startswith('ERROR'):
    text = extract_text(html)
    print('=== ABOUT PAGE (first 1500 chars) ===')
    print(text[:1500])
else:
    print('About page error:', html)

print('\n\n')

# Get services pages
for page in ['kitchen-remodeling', 'bathroom-remodeling', 'custom-countertops']:
    html = fetch(f'https://www.letsremodel.net/{page}/')
    if not html.startswith('ERROR'):
        text = extract_text(html)
        print(f'=== {page.upper()} (first 500 chars) ===')
        print(text[:500])
        print()

# Now extract the rating details from main page more carefully
html = fetch('https://www.letsremodel.net')
if not html.startswith('ERROR'):
    text = extract_text(html)
    # Find all rating patterns
    ratings = re.findall(r'Rated\s+([\d.]+)\s+out\s+of\s+5\s+([\d.]+)\s+avg\.\s*rating\s*\(([\d,]+)\s*reviews?\)', text)
    print('\n=== ALL RATINGS FOUND ===')
    for r in ratings:
        print(f'  Rating: {r[0]}/5, Avg: {r[1]}, Reviews: {r[2]}')
    
    # Look for platform names near ratings (Houzz, Google, Yelp, etc.)
    rating_section = ''
    idx = text.lower().find('rated')
    if idx > -1:
        rating_section = text[max(0,idx-100):idx+600]
        print('\n=== RATING SECTION CONTEXT ===')
        print(rating_section)
    
    # License info
    or_lic = re.findall(r'OR\s*(\d{5,})', text)
    wa_lic = re.findall(r'WA\s*([A-Z]+\*?\w+)', text)
    print(f'\nOR License: {or_lic}')
    print(f'WA License: {wa_lic}')
