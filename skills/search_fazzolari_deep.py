import urllib.request
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Check fazzhomes.com
urls = [
    ('Main Website', 'https://www.fazzhomes.com'),
    ('Angi Reviews', 'https://www.angi.com/companylist/us/wa/vancouver/fazzolari-custom-homes-and-renovations-reviews-5529634.htm'),
    ('BuildZoom', 'https://www.buildzoom.com/contractor/fazzolari-custom-homes-inc-or'),
    ('Houzz', 'https://www.houzz.com/professionals/design-build-firms/fazzolari-construction-pfvwus-pf~553791893'),
    ('BBB Search', 'https://html.duckduckgo.com/html/?q=Fazzolari+Custom+Homes+Vancouver+WA+BBB+rating'),
    ('Yelp Search', 'https://html.duckduckgo.com/html/?q=Fazzolari+Custom+Homes+Vancouver+WA+yelp+reviews+rating'),
    ('Google Rating Search', 'https://html.duckduckgo.com/html/?q=Fazzolari+Custom+Homes+Vancouver+WA+google+reviews+rating+stars'),
]

for label, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            clean = re.sub(r'<[^>]+>', ' ', html)
            clean = re.sub(r'\s+', ' ', clean)
            
            # Extract relevant snippets
            keywords = ['fazzolari', 'rating', 'review', 'star', 'remodel', 'bathroom', 'kitchen', 'service', 'license', 'phone', '360-571', 'award', 'custom home', 'renovation']
            sentences = re.split(r'[.!\n]', clean)
            relevant = []
            for s in sentences:
                sl = s.lower()
                if any(k in sl for k in keywords):
                    stripped = s.strip()
                    if len(stripped) > 15 and len(stripped) < 300:
                        relevant.append(stripped)
            
            print(f"\n=== {label} ({url[:60]}) ===")
            seen = set()
            count = 0
            for r in relevant:
                if r not in seen and count < 15:
                    seen.add(r)
                    print(f"  - {r[:250]}")
                    count += 1
            
            # Look for ratings patterns like "4.5/5" or "4.5 stars" or "X reviews"
            rating_patterns = re.findall(r'[\d.]+\s*(?:/\s*5|stars?|out of 5)', clean, re.IGNORECASE)
            review_counts = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', clean, re.IGNORECASE)
            if rating_patterns:
                print(f"  Ratings found: {rating_patterns[:5]}")
            if review_counts:
                print(f"  Review counts: {review_counts[:5]}")
                
    except Exception as e:
        print(f"\n=== {label}: Error - {str(e)[:100]} ===")

print("\n=== Deep search complete ===")
