import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get services page
print('=== SERVICES PAGE ===')
resp = requests.get('https://www.mountainwoodhomes.com/services/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text(separator='\n', strip=True)
for line in text.split('\n'):
    line = line.strip()
    if len(line) > 10 and len(line) < 300:
        print(line)

# Get contact/about page for phone number
print('\n=== ABOUT PAGE ===')
resp = requests.get('https://www.mountainwoodhomes.com/about/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text(separator='\n', strip=True)
# Look for phone numbers
phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
print('Phone numbers found:', phones)
# Look for license/CCB
licenses = re.findall(r'(?:CCB|license|lic)[#:\s]*(\d+)', text, re.IGNORECASE)
print('License numbers found:', licenses)
for line in text.split('\n'):
    line = line.strip()
    if any(kw in line.lower() for kw in ['phone', 'call', 'ccb', 'license', 'lic#', 'bonded', 'insured']):
        print(f'  >> {line[:200]}')

# Check footer of main page for phone/license
print('\n=== FOOTER INFO ===')
resp = requests.get('https://www.mountainwoodhomes.com/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
footer = soup.find('footer')
if footer:
    ft = footer.get_text(separator='\n', strip=True)
    for line in ft.split('\n'):
        line = line.strip()
        if len(line) > 3:
            print(f'  {line}')
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', ft)
    print('Footer phones:', phones)
    licenses = re.findall(r'(?:CCB|license|lic)[#:\s]*(\d+)', ft, re.IGNORECASE)
    print('Footer licenses:', licenses)

# Also check all tel: links
all_tel = soup.find_all('a', href=re.compile(r'tel:'))
print('\nTel links:', [a.get('href') for a in all_tel])

# Check awards page
print('\n=== AWARDS PAGE ===')
resp = requests.get('https://www.mountainwoodhomes.com/about/awards/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text(separator='\n', strip=True)
for line in text.split('\n'):
    line = line.strip()
    if len(line) > 10 and len(line) < 300 and any(kw in line.lower() for kw in ['award', 'bbb', 'houzz', 'nari', 'association', 'member', 'certified', 'accredited']):
        print(f'  {line}')
