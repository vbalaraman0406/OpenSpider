import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Try Google Maps search
queries = [
    'https://www.google.com/maps/search/Let%27s+Remodel+Vancouver+WA+98662',
    'https://www.google.com/maps/search/Lets+Remodel+bathroom+Vancouver+WA',
    # Try yellowpages
    'https://www.yellowpages.com/vancouver-wa/lets-remodel',
    # Try mapquest
    'https://www.mapquest.com/search/results?query=Let%27s+Remodel&location=Vancouver+WA+98662',
    # Try nextdoor business search
    'https://nextdoor.com/pages/lets-remodel-vancouver-wa/',
    # Try homeadvisor
    'https://www.homeadvisor.com/rated.LetsRemodel.html',
    # Try with phone number variations
    'https://www.google.com/search?q=%22lets+remodel%22+%22360%22+vancouver+wa+bathroom',
    'https://www.google.com/search?q=%22lets+remodel%22+%22503%22+vancouver+wa+bathroom',
    # Try WA L&I contractor search
    'https://fortress.wa.gov/lni/bbip/Search.aspx?BusinessName=lets+remodel&City=vancouver',
]

for url in queries:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract useful info
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)
        # Look for ratings
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', html, re.I)
        # Look for addresses with 98662
        addresses = re.findall(r'[^<>]{0,50}98662[^<>]{0,50}', html)
        # Look for 'remodel' mentions
        remodel_mentions = re.findall(r'[^<>]{0,80}[Rr]emodel[^<>]{0,80}', html)
        
        print(f'\n=== {url[:80]} ===')
        print(f'Status: {resp.status}')
        print(f'Phones: {phones[:5]}')
        print(f'Ratings: {ratings[:3]}')
        print(f'Addresses: {addresses[:3]}')
        print(f'Remodel mentions: {len(remodel_mentions)}')
        if remodel_mentions:
            for m in remodel_mentions[:5]:
                print(f'  -> {m.strip()[:100]}')
    except Exception as e:
        print(f'\n=== {url[:80]} ===')
        print(f'Error: {e}')

print('\nDone with search round 9')