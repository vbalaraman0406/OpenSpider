import requests
import re
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_article(name, url):
    print(f'\n=== {name} ===')
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        html = resp.text
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Extract paragraph text
        paras = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        for p in paras:
            t = re.sub(r'<[^>]+>', '', p).strip()
            t = re.sub(r'\s+', ' ', t)
            if len(t) > 40:
                print(t[:500])
                print()
    except Exception as e:
        print(f'Error: {e}')

# Key articles to fetch
fetch_article('NDTV - TN Election Date', 'https://www.ndtv.com/india-news/tamil-nadu-election-date-2026')
fetch_article('Opinion Polls', 'https://www.google.com/search?q=Tamil+Nadu+2026+election+opinion+poll+DMK+AIADMK+BJP+seat+prediction')
fetch_article('Alliance Updates', 'https://www.google.com/search?q=Tamil+Nadu+2026+election+alliance+DMK+AIADMK+BJP+TVK+Vijay')

print('\nDONE')
