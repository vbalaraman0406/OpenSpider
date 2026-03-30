import json

with open('redfin_results.json', 'r') as f:
    results = json.load(f)

print(f"Total results: {len(results)}")

# Count by bed count
from collections import Counter
bed_counts = Counter()
bath_counts = Counter()
year_counts = Counter()

for r in results:
    try:
        beds = int(r.get('beds', 0)) if r.get('beds') else 0
        baths = float(r.get('baths', 0)) if r.get('baths') else 0
        year = int(r.get('year', 0)) if r.get('year') else 0
        price = float(r.get('price', 0)) if r.get('price') else 0
    except:
        beds = 0
        baths = 0
        year = 0
        price = 0
    bed_counts[beds] += 1
    bath_counts[baths] += 1
    if year >= 2017:
        year_counts[year] += 1

print(f"\nBed counts: {sorted(bed_counts.items())}")
print(f"Bath counts: {sorted(bath_counts.items())}")
print(f"Year 2017+ counts: {sorted(year_counts.items())}")

# Show all listings with 4+ beds
print("\n=== Listings with 4+ beds ===")
for r in results:
    try:
        beds = int(r.get('beds', 0)) if r.get('beds') else 0
    except:
        beds = 0
    if beds >= 4:
        print(f"  ${r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year']} | {r['address']}")

# Show sample of data
print("\n=== First 3 raw entries ===")
for r in results[:3]:
    print(json.dumps(r, indent=2))
