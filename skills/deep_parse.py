import re

with open('/Users/vbalaraman/OpenSpider/rotowire.html', 'r', errors='ignore') as f:
    html = f.read()

# Extract news update blocks - look for player names and their updates
# RotoWire typically has news-update divs with player info
pattern = r'class="news-update[^"]*"[\s\S]*?</div>'
blocks = re.findall(pattern, html[:200000], re.IGNORECASE)
print(f'News blocks found: {len(blocks)}')

# Try another approach - extract all text between specific markers
# Look for date markers and player names
player_news = re.findall(r'<a[^>]*href="/baseball/player[^"]*"[^>]*>([^<]+)</a>', html)
print(f'\nPlayer mentions ({len(player_news)}):')
for p in player_news[:40]:
    print(f'  {p.strip()}')

# Extract news snippets - text after player names
snippets = re.findall(r'<div[^>]*class="[^"]*news-update__headline[^"]*"[^>]*>([^<]+)</div>', html)
print(f'\nHeadlines ({len(snippets)}):')
for s in snippets[:30]:
    print(f'  {s.strip()}')

# Try to find news text content
news_text = re.findall(r'<p[^>]*>([^<]{30,300})</p>', html)
print(f'\nParagraphs with content ({len(news_text)}):')
for t in news_text[:25]:
    clean = t.strip()
    if any(word in clean.lower() for word in ['injury', 'il', 'roster', 'start', 'pitch', 'hit', 'homer', 'return', 'placed', 'activated', 'waiver', 'trade', 'call', 'option', 'demotion']):
        print(f'  {clean}')
