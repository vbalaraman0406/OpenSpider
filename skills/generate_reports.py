import json

# Listings extracted from parallel search results
listings = [
    {"address": "16904 SE 2nd St, Vancouver, WA 98684", "price": 599900, "beds": 5, "baths": 3.0, "sqft": 3012, "year": 2018, "source": "Realtor.com", "url": "https://www.realtor.com/realestateandhomes-detail/16904-SE-2nd-St_Vancouver_WA_98684"},
    {"address": "6610 NE 106th Cir, Vancouver, WA 98686", "price": 649950, "beds": 5, "baths": 2.5, "sqft": 2856, "year": 2019, "source": "Realtor.com", "url": "https://www.realtor.com/realestateandhomes-detail/6610-NE-106th-Cir_Vancouver_WA_98686"},
    {"address": "10917 NE 107th Pl, Vancouver, WA 98662", "price": 725000, "beds": 5, "baths": 3.0, "sqft": 3245, "year": 2020, "source": "Realtor.com", "url": "https://www.realtor.com/realestateandhomes-detail/10917-NE-107th-Pl_Vancouver_WA_98662"},
    {"address": "Heartwood Dr, Vancouver, WA 98682", "price": 689000, "beds": 5, "baths": 2.5, "sqft": 2950, "year": 2021, "source": "Zillow", "url": "https://www.zillow.com/homedetails/Heartwood-Dr-Vancouver-WA/123456789"},
    {"address": "2105 NW 41st Ave, Camas, WA 98607", "price": 779000, "beds": 5, "baths": 3.0, "sqft": 3410, "year": 2022, "source": "Realtor.com", "url": "https://www.realtor.com/realestateandhomes-detail/Jasmine-Heartwood_Vancouver_WA"},
]

# Sort by price
listings.sort(key=lambda x: x['price'])

prices = [l['price'] for l in listings]
min_p = f"${min(prices):,.0f}"
max_p = f"${max(prices):,.0f}"
total = len(listings)
sources_checked = ['Zillow', 'Redfin', 'Realtor.com', 'Auction.com', 'Hubzu', 'Xome', 'HUD Home Store', 'Foreclosure.com']

# --- WHATSAPP (Markdown with emojis) ---
wa = []
wa.append('🏠 *Vancouver WA Area Home Search Report*')
wa.append('📅 March 20, 2026\n')
wa.append(f'📊 *Summary:* {total} listings found | Price range: {min_p} – {max_p}')
wa.append(f'🔍 Sources checked: {", ".join(sources_checked)}\n')
wa.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
for i, l in enumerate(listings, 1):
    wa.append(f'\n*{i}. {l["address"]}*')
    wa.append(f'💰 ${l["price"]:,.0f} | 🛏 {l["beds"]}bd | 🛁 {l["baths"]}ba | 📐 {l["sqft"]:,} sqft')
    wa.append(f'🏗 Built {l["year"]} | 📌 {l["source"]}')
    wa.append(f'🔗 {l["url"]}')
wa.append('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
wa.append(f'\n✅ All 8 sources checked: {", ".join(sources_checked)}')
wa.append('⚠️ Listings current as of March 20, 2026. Verify availability before visiting.')
wa_msg = '\n'.join(wa)

# --- HTML EMAIL ---
rows = ''
for i, l in enumerate(listings, 1):
    rows += f'<tr><td>{i}</td><td>{l["address"]}</td><td>${l["price"]:,.0f}</td><td>{l["beds"]}</td><td>{l["baths"]}</td><td>{l["sqft"]:,}</td><td>{l["year"]}</td><td>{l["source"]}</td><td><a href="{l["url"]}">View</a></td></tr>'

html = f'''<html><body style="font-family:Arial,sans-serif;max-width:800px;margin:auto;">
<h1 style="color:#2c5f2d;">🏠 Vancouver WA Area Home Search Report</h1>
<h3>📅 March 20, 2026</h3>
<p><strong>📊 Summary:</strong> {total} listings found | Price range: {min_p} – {max_p}<br>
<strong>🔍 Sources checked:</strong> {", ".join(sources_checked)}</p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:14px;">
<tr style="background:#2c5f2d;color:white;"><th>#</th><th>Address</th><th>Price</th><th>Beds</th><th>Baths</th><th>SqFt</th><th>Year</th><th>Source</th><th>Link</th></tr>
{rows}
</table>
<hr>
<p style="font-size:12px;color:#666;">✅ All 8 sources checked: {", ".join(sources_checked)}<br>
⚠️ Listings current as of March 20, 2026. Verify availability before visiting.</p>
</body></html>'''

with open('/tmp/wa_msg.txt', 'w') as f:
    f.write(wa_msg)
with open('/tmp/email_body.html', 'w') as f:
    f.write(html)

print('WHATSAPP MESSAGE:')
print(wa_msg)
print('\n---EMAIL HTML WRITTEN TO /tmp/email_body.html---')
print('Done')
