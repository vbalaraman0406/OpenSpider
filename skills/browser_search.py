# This script will generate Google search URLs for each source
# We'll use the browser to search each one

sources = [
    ('Zillow', 'zillow.com vancouver wa 5 bedroom house for sale under 600000'),
    ('Redfin', 'redfin.com vancouver wa 5 bedroom 2.5 bath house for sale'),
    ('Realtor.com', 'realtor.com vancouver wa 5 bedroom house for sale'),
    ('HUD Home Store', 'hudhomestore.gov washington vancouver'),
    ('Foreclosure.com', 'foreclosure.com vancouver wa'),
    ('Auction.com', 'auction.com vancouver wa houses'),
    ('Hubzu', 'hubzu.com vancouver wa'),
    ('Xome', 'xome.com vancouver wa'),
]

for source, query in sources:
    url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
    print(f'{source}: {url}')
