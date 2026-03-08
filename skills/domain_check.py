import whois

domains = ['pitwall.ai', 'pitwallf1.com', 'pitwall.io', 'pitwalldata.com', 'pitwall.app']

for domain in domains:
    try:
        w = whois.whois(domain)
        if w.domain_name:
            reg = w.registrar if w.registrar else 'Unknown'
            exp = str(w.expiration_date)[:10] if w.expiration_date else 'Unknown'
            print(f'{domain}: TAKEN | Registrar: {reg} | Expires: {exp}')
        else:
            print(f'{domain}: LIKELY AVAILABLE')
    except Exception as e:
        err_str = str(e).lower()
        if 'no match' in err_str or 'not found' in err_str or 'no entries' in err_str or 'no data' in err_str:
            print(f'{domain}: AVAILABLE')
        else:
            print(f'{domain}: CHECK MANUALLY (Error: {str(e)[:80]})')
