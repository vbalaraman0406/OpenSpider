import requests
from bs4 import BeautifulSoup
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

contractors = [
    'NW Tub and Shower Vancouver WA reviews phone',
    'TGR General Construction Vancouver WA bathroom remodel reviews',
    'Reliable Men Construction Vancouver WA bathroom tile reviews',
    'Elegant Tile and Hardwood Floors Vancouver WA reviews phone',
    'Rapid Bath and Construction Vancouver WA reviews',
    'Columbia River Tile and Stone Vancouver WA reviews phone',
    'SingleTrack Construction Vancouver WA bathroom reviews',
    'Absolute Tile Corporation Vancouver WA 98662 reviews phone',
    'VDC Builders Inc Vancouver WA bathroom remodel reviews',
    'Mr Handyman Vancouver Camas Ridgefield WA bathroom remodel reviews',
]

for query in contractors:
    try:
        url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}'
        print(f'\n{"="*80}')
        print(f'Searching: {query}')
        print('='*80)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result')
            for r in results[:5]:
                title_tag = r.find('a', class_='result__a')
                snippet_tag = r.find('a', class_='result__snippet')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href', '')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
                    print(f'\n  Title: {title}')
                    # Extract clean URL
                    if 'uddg=' in link:
                        clean_url = requests.utils.unquote(link.split('uddg=')[1].split('&')[0])
                    else:
                        clean_url = link
                    print(f'  URL: {clean_url}')
                    print(f'  Snippet: {snippet[:250]}')
        else:
            print(f'  Status: {response.status_code}')
        time.sleep(2)
    except Exception as e:
        print(f'  Error: {e}')
