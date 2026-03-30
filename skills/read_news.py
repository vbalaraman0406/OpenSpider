with open('/tmp/iran_news.xml', 'r') as f:
    data = f.read()

import re
titles = re.findall(r'<title>(.*?)</title>', data)
pub_dates = re.findall(r'<pubDate>(.*?)</pubDate>', data)
sources = re.findall(r'<source[^>]*>(.*?)</source>', data)

print(f'Total titles found: {len(titles)}')
print(f'Total dates found: {len(pub_dates)}')
print(f'Total sources found: {len(sources)}')
print()

for i, title in enumerate(titles[1:15]):
    src = sources[i] if i < len(sources) else 'Unknown'
    date = pub_dates[i] if i < len(pub_dates) else 'Unknown'
    print(f'{i+1}. [{src}] {title}')
    print(f'   Date: {date}')
    print()
