import requests
from bs4 import BeautifulSoup

def scrape_hackernews():
    url = 'https://news.ycombinator.com'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Hacker News uses <span class="titleline"> containing an <a> tag for each story
    titleline_spans = soup.select('span.titleline > a')
    
    stories = []
    for a_tag in titleline_spans[:30]:
        title = a_tag.get_text(strip=True)
        link = a_tag.get('href', '')
        # Some HN links are relative (e.g., "item?id=...")
        if link and not link.startswith('http'):
            link = f'https://news.ycombinator.com/{link}'
        stories.append({'title': title, 'url': link})
    
    # Print results in a structured format
    print('=' * 80)
    print(f'{"HACKER NEWS - TOP STORIES":^80}')
    print('=' * 80)
    print()
    
    for i, story in enumerate(stories, 1):
        print(f'{i:2}. {story["title"]}')
        print(f'    URL: {story["url"]}')
        print()
    
    print('=' * 80)
    print(f'Total stories scraped: {len(stories)}')
    print('=' * 80)

if __name__ == '__main__':
    scrape_hackernews()
