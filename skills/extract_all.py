import json

with open('market_data.json', 'r') as f:
    data = json.load(f)

for cat in data:
    print(f'\n=== {cat} ===')
    for sym, info in data[cat].items():
        p = info.get('price','N/A')
        chg = info.get('change_percent','N/A')
        vol = info.get('volume','N/A')
        mcap = info.get('market_cap','N/A')
        h52 = info.get('52_week_high','N/A')
        l52 = info.get('52_week_low','N/A')
        pe = info.get('pe_ratio','N/A')
        d50 = info.get('50_day_avg','N/A')
        d200 = info.get('200_day_avg','N/A')
        beta = info.get('beta','N/A')
        name = info.get('name','N/A')
        print(f'{sym}|{name}|{p}|{chg}%|{vol}|{mcap}|{pe}|{h52}|{l52}|{d50}|{d200}|{beta}')
