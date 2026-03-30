import json

with open('redfin_results.json', 'r') as f:
    results = json.load(f)

print(f"Total results from Redfin: {len(results)}")

# Filter for 5+ beds, 2.5-3 baths, built 2017+, under $600K
filtered = []
for r in results:
    try:
        beds = int(r.get('beds', 0)) if r.get('beds') else 0
        baths = float(r.get('baths', 0)) if r.get('baths') else 0
        year = int(r.get('year', 0)) if r.get('year') else 0
        price = float(r.get('price', 0)) if r.get('price') else 0
    except:
        continue
    
    if beds >= 5 and 2.5 <= baths <= 3.0 and year >= 2017 and price <= 600000 and price > 0:
        filtered.append(r)
        print(f"MATCH: ${r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year']} | {r['address']} | {r['url']}")

print(f"\nFiltered results (5+bd, 2.5-3ba, 2017+, <$600K): {len(filtered)}")

# Also show 5+ bed results with any bath count for reference
print("\n=== All 5+ bed results (any bath count) ===")
for r in results:
    try:
        beds = int(r.get('beds', 0)) if r.get('beds') else 0
        year = int(r.get('year', 0)) if r.get('year') else 0
        price = float(r.get('price', 0)) if r.get('price') else 0
    except:
        continue
    if beds >= 5 and year >= 2017 and price <= 600000 and price > 0:
        print(f"  ${r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year']} | {r['address']} | {r['url']}")

# Save filtered results
with open('redfin_filtered.json', 'w') as f:
    json.dump(filtered, f, indent=2)
print(f"\nSaved {len(filtered)} filtered results to redfin_filtered.json")
