import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    ('Brave', 'https://search.brave.com/search?q=Beto+and+Son+Remodeling+LLC+Vancouver+WA+reviews+rating+phone'),
    ('MapQuest', 'https://www.mapquest.com/us/washington/beto-son-remodeling-543368883'),
    ('TownPlanner', 'https://townplanner.com/directory/229341'),
    ('HomeYou', 'https://homeyou.com/beto-son-remodeling-vancouver-wa'),
    ('BizProfile', 'https://bizprofile.net/home/washi'),
]

for name, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        text = BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)
        # Search for rating patterns, phone numbers, addresses
        ratings = re.findall(r'(\d\.\d)\s*(?:star|out of|/\s*5|rating)', text, re.I)
        phones = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
        # Find review counts
        reviews = re.findall(r'(\d+)\s*(?:review|rating)', text, re.I)
        
        # Extract relevant snippet around 'Beto'
        beto_idx = text.lower().find('beto')
        snippet = ''
        if beto_idx >= 0:
            snippet = text[max(0,beto_idx-100):beto_idx+500]
        
        print(f'\n=== {name} ===')
        print(f'Status: {r.status_code}')
        print(f'Ratings found: {ratings}')
        print(f'Phones found: {phones}')
        print(f'Reviews found: {reviews}')
        print(f'Snippet: {snippet[:600]}')
    except Exception as e:
        print(f'\n=== {name} === ERROR: {e}')
