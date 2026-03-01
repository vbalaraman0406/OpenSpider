import requests
from bs4 import BeautifulSoup

query = 'Fazzolari bathroom remodel contractor Vancouver WA 98662'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try DuckDuckGo HTML search
url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}'
print(f'Searching: {url}')
resp = requests.get(url, headers=headers, timeout=15)
print(f'Status: {resp.status_code}')

soup = BeautifulSoup(resp.text, 'html.parser')
results = soup.find_all('div', class_='result')
print(f'Found {len(results)} results\n')

for i, r in enumerate(results[:10]):
    title_tag = r.find('a', class_='result__a')
    snippet_tag = r.find('a', class_='result__snippet')
    title = title_tag.get_text(strip=True) if title_tag else 'N/A'
    link = title_tag.get('href', 'N/A') if title_tag else 'N/A'
    snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'N/A'
    print(f'--- Result {i+1} ---')
    print(f'Title: {title}')
    print(f'Link: {link}')
    print(f'Snippet: {snippet}')
    print()
