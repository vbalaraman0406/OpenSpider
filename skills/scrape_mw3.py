import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get contact page - look for phone, address, email
resp = requests.get('https://www.mountainwoodhomes.com/contact/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
for script in soup(['script', 'style', 'nav', 'header']):
    script.decompose()
text = soup.get_text(separator='\n', strip=True)

# Find phone numbers
phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
print('PHONES:', phones)

# Find emails
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
print('EMAILS:', emails)

# Find addresses (look for common patterns)
address_patterns = re.findall(r'\d+\s+[\w\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct|Hwy|Suite|Ste)[\w\s,]*\d{5}', text)
print('ADDRESSES:', address_patterns)

# Look for links with tel: or mailto:
resp2 = requests.get('https://www.mountainwoodhomes.com/contact/', headers=headers, timeout=10)
soup2 = BeautifulSoup(resp2.text, 'html.parser')
tel_links = soup2.find_all('a', href=re.compile(r'tel:'))
for t in tel_links:
    print('TEL LINK:', t.get('href'), t.get_text(strip=True))

mail_links = soup2.find_all('a', href=re.compile(r'mailto:'))
for m in mail_links:
    print('MAIL LINK:', m.get('href'), m.get_text(strip=True))

# Get footer content which often has contact info
footer = soup2.find('footer')
if footer:
    ftext = footer.get_text(separator='\n', strip=True)
    print('\nFOOTER:')
    print(ftext[:800])

# Now get the why-us page content (skip nav)
print('\n=== WHY US PAGE ===')
resp3 = requests.get('https://www.mountainwoodhomes.com/why-us/', headers=headers, timeout=10)
soup3 = BeautifulSoup(resp3.text, 'html.parser')
for script in soup3(['script', 'style', 'nav', 'header']):
    script.decompose()
main = soup3.find('main') or soup3.find('div', class_=re.compile(r'content|main'))
if main:
    mtext = main.get_text(separator='\n', strip=True)
    lines = [l for l in mtext.split('\n') if l.strip()]
    print('\n'.join(lines[:40]))

# Awards page
print('\n=== AWARDS PAGE ===')
resp4 = requests.get('https://www.mountainwoodhomes.com/awards-associations/', headers=headers, timeout=10)
soup4 = BeautifulSoup(resp4.text, 'html.parser')
for script in soup4(['script', 'style', 'nav', 'header']):
    script.decompose()
main4 = soup4.find('main') or soup4.find('div', class_=re.compile(r'content|main'))
if main4:
    mtext4 = main4.get_text(separator='\n', strip=True)
    lines4 = [l for l in mtext4.split('\n') if l.strip()]
    print('\n'.join(lines4[:40]))
