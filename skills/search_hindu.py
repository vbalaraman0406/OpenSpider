import requests
import re
import html as h

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

queries = [
    ('TN Election 2026', 'Tamil+Nadu+election+2026+site%3Athehindu.com'),
    ('TN Assembly DMK AIADMK', 'Tamil+Nadu+2026+assembly+election+DMK+AIADMK+site%3Athehindu.com'),
    ('TN Opinion Poll', 'Tamil+Nadu+election+opinion+poll+2026+site%3Athehindu.com'),
]

for label, q in queries:
    url = 'https://www.google.com/search?q=' + q + '&num=10'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        links = re.findall(r'/url\?q=(https?://[^&]*thehindu\.com[^&]*)&', r.text)
        unique = list(dict.fromkeys(links))[:6]
        print('=== ' + label + ' ===')
        for link in unique:
            print('  ' + h.unescape(link))
        if not unique:
            print('  No results found')
        print()
    except Exception as e:
        print('Error for ' + label + ': ' + str(e))
