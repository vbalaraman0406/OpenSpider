import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Brave search for rating info
queries = [
    'Beto and Son Remodeling LLC reviews rating Vancouver WA',
    'Beto and Son Remodeling LLC google reviews',
    'site:google.com/maps Beto and Son Remodeling Vancouver WA'
]

for q in queries:
    try:
        url = f'https://search.brave.com/search?q={q.replace(" ", "+")}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get all text snippets
        snippets = soup.find_all(['p', 'span', 'div'], string=lambda t: t and ('rating' in t.lower() or 'star' in t.lower() or 'review' in t.lower() or '4.' in t or '5.' in t))
        print(f'\n=== Query: {q} ===')
        for s in snippets[:10]:
            text = s.get_text(strip=True)[:200]
            print(text)
        # Also check for any rating-like patterns
        import re
        text = soup.get_text()
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of|/5)', text, re.IGNORECASE)
        reviews = re.findall(r'(\d+)\s*(?:review|rating)', text, re.IGNORECASE)
        if ratings:
            print(f'RATINGS FOUND: {ratings}')
        if reviews:
            print(f'REVIEWS FOUND: {reviews}')
    except Exception as e:
        print(f'Error: {e}')

# Try Google Maps direct
try:
    url = 'https://www.google.com/maps/search/Beto+and+Son+Remodeling+Vancouver+WA'
    r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    import re
    ratings = re.findall(r'(\d\.\d)\s*star', r.text, re.IGNORECASE)
    reviews = re.findall(r'(\d+)\s*review', r.text, re.IGNORECASE)
    print(f'\n=== Google Maps ===')
    print(f'Ratings: {ratings}')
    print(f'Reviews: {reviews}')
except Exception as e:
    print(f'Google Maps error: {e}')

# Try HomeYou page
try:
    url = 'https://www.homeadvisor.com/rated.BetoandssonRemodeling.75498186.html'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'\n=== HomeAdvisor Status: {r.status_code} ===')
except Exception as e:
    print(f'HomeAdvisor error: {e}')

# Try WA L&I lookup
try:
    url = 'https://secure.lni.wa.gov/verify/Results.aspx?k=Beto+and+Son&t=C'
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('td')
    print(f'\n=== WA L&I ===')
    for td in results[:20]:
        print(td.get_text(strip=True))
except Exception as e:
    print(f'L&I error: {e}')
