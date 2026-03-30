from bs4 import BeautifulSoup
import sys

html_content = sys.stdin.read()
soup = BeautifulSoup(html_content, 'html.parser')

link = soup.find('a', string=lambda text: text and 'Iran hardliners rally behind new leader' in text)

if link and 'href' in link.attrs:
    print(link['href'])
else:
    print('Link not found')
