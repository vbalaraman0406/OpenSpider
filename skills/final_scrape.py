import urllib.request
import json
import re

# Try SerpAPI-style free search or just use what we have
# Let's try a simple Google search with a very realistic browser UA
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

urls = [
    ('Yelp', 'https://www.yelp.com/search?find_desc=bathroom+remodel&find_loc=Vancouver%2C+WA+98662'),
    ('Thumbtack', 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'),
    ('HomeAdvisor', 'https://www.homeadvisor.com/rated.BathroomRemodel.Vancouver.WA.html'),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract business names and ratings
        # Look for common patterns
        if 'yelp' in url:
            # Find business names
            biz = re.findall(r'"name":"([^"]+)"', html)
            ratings = re.findall(r'"rating":([\d.]+)', html)
            phones = re.findall(r'"phone":"([^"]+)"', html)
            print(f'Yelp businesses: {biz[:10]}')
            print(f'Yelp ratings: {ratings[:10]}')
            print(f'Yelp phones: {phones[:10]}')
        elif 'thumbtack' in url:
            biz = re.findall(r'"businessName":"([^"]+)"', html)
            ratings = re.findall(r'"averageRating":([\d.]+)', html)
            reviews = re.findall(r'"numReviews":(\d+)', html)
            print(f'Thumbtack businesses: {biz[:10]}')
            print(f'Thumbtack ratings: {ratings[:10]}')
            print(f'Thumbtack reviews: {reviews[:10]}')
        else:
            # Generic extraction
            biz = re.findall(r'"name":"([^"]+)"', html)
            print(f'{name} businesses: {biz[:10]}')
        print(f'{name}: OK ({len(html)} chars)')
    except Exception as e:
        print(f'{name}: Error - {e}')
        # Try to get partial data
        continue

print('\n--- Done ---')
