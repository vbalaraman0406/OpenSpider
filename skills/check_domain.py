import whois

try:
    w = whois.whois('pitwall.ai')
    print('=== WHOIS RESULTS FOR pitwall.ai ===')
    print(f'Domain: {w.domain_name}')
    print(f'Registrar: {w.registrar}')
    print(f'Creation Date: {w.creation_date}')
    print(f'Expiration Date: {w.expiration_date}')
    print(f'Name Servers: {w.name_servers}')
    print(f'Status: {w.status}')
    print(f'Org: {w.org}')
    print(f'Emails: {w.emails}')
except Exception as e:
    print(f'WHOIS lookup failed: {e}')

alternatives = ['pitwalldata.ai', 'pitwall.io', 'thepitwall.ai', 'pitwallf1.com', 'pitwall.app']
print('\n=== ALTERNATIVE DOMAIN CHECKS ===')
for domain in alternatives:
    try:
        w2 = whois.whois(domain)
        if w2.domain_name:
            print(f'{domain}: TAKEN (registrar: {w2.registrar})')
        else:
            print(f'{domain}: POSSIBLY AVAILABLE')
    except Exception as e:
        print(f'{domain}: POSSIBLY AVAILABLE (error: {str(e)[:60]})')
