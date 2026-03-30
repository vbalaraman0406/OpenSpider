report = """# 🏠 5-Bedroom Home Listings — Vancouver WA Area
## Search Criteria
- **Bedrooms:** 5
- **Bathrooms:** 2.5–3
- **Max Price:** $800,000
- **Year Built:** 2017 or newer
- **Areas:** Vancouver, Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie (all WA)
- **Sources Checked:** Zillow, Realtor.com
- **Date:** March 21, 2026

---

## Vancouver, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 1 | The 2167 Plan, Stone's Throw (New Construction) | $514,960+ | 5 | 3 | 2,167 | 2026 | Zillow |
| 2 | 13314 NE 112th St, Vancouver, WA 98686 | $654,990 | 5 | 3 | ~2,600 | 2020 | Realtor.com |
| 3 | 6610 NE 106th Cir, Vancouver, WA 98682 | $660,000 | 5 | 2.5 | 2,582 | 2018 | Zillow/Realtor.com |
| 4 | The 2676 Plan, Ramble Creek (New Construction) | $699,960 | 5 | 3 | 2,676 | 2026 | Realtor.com |
| 5 | 6901 NE 16th Ave, Vancouver, WA | $719,000 | 5 | 3 | 3,185 | 2019 | Realtor.com |
| 6 | 12500 NE 107th Way, Vancouver, WA 98682 | $729,900 | 5 | 3 | 2,958 | 2019 | Zillow |
| 7 | 10917 NE 107th Pl, Vancouver, WA 98682 | $761,260 | 5 | 3 | ~2,800 | 2019 | Realtor.com |
| 8 | 10810 NE 111th St, Vancouver, WA 98682 | $762,360 | 5 | 3 | 2,664 | 2020 | Realtor.com |
| 9 | 915 NE 146th St, Vancouver, WA 98685 | $799,000 | 5 | 3 | 2,454 | 2019 | Zillow |

## Ridgefield, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 10 | 3910 S Hay Field Cir, Ridgefield, WA 98642 | $724,950 | 5 | 3 | 2,405 | 2020 | Zillow |

## Battle Ground, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 11 | Oakridge Plan, Woodin Creek Station (New Construction) | $624,999+ | 5 | 3 | 2,650 | 2026 | Zillow |
| 12 | 3438 SE 8th Ave, Battle Ground, WA 98604 | $648,900 | 5 | 3 | 2,327 | 2021 | Zillow |
| 13 | 3111 SW 4th Ave, Battle Ground, WA 98604 (New Construction) | $653,999 | 5 | 3 | 2,650 | 2026 | Zillow |
| 14 | 1577 NE 9th Ave, Battle Ground, WA 98604 | $679,900 | 5 | 3 | 2,776 | 2020 | Zillow |
| 15 | 755 NW 29th St, Battle Ground, WA 98604 (New Construction) | $685,600 | 5 | 3 | 2,664 | 2026 | Zillow |
| 16 | 771 NW 29th St, Battle Ground, WA 98604 (New Construction) | $691,800 | 5 | 3 | 2,664 | 2026 | Zillow |
| 17 | 2801 NW 8th Ave, Battle Ground, WA 98604 (New Construction) | $696,000 | 5 | 3 | 2,664 | 2026 | Zillow |

## Camas, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 18 | 9341 N Alder St, Camas, WA 98607 | $639,900 | 5 | 3 | 2,219 | 2020 | Zillow |
| 19 | 9465 N Alder St, Camas, WA 98607 | $649,000 | 5 | 3 | 2,298 | 2020 | Zillow |

## Washougal, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 20 | 292 W Maple St, Washougal, WA 98671 | $719,900 | 5 | 3 | 2,339 | 2019 | Zillow |

## Brush Prairie, WA

| # | Address | Price | Beds | Baths | Sqft | Year Built | Source |
|---|---------|-------|------|-------|------|------------|--------|
| 21 | 11112 NE 131st Ave, Brush Prairie, WA 98606 | $639,990 | 5 | 3 | 2,660 | 2020 | Zillow |
| 22 | The 2414 Plan, Heartwood (New Construction) | $659,960+ | 5 | 3 | 2,414 | 2026 | Zillow |

---

## Summary
- **Total Matching Listings Found:** 22
- **Price Range:** $514,960 – $799,000
- **Most Listings:** Battle Ground, WA (7) and Vancouver, WA (9)
- **New Construction:** 8 listings (Stone's Throw, Woodin Creek Station, Heartwood, Ramble Creek, and others)

## Sources Checked
- ✅ Zillow — Primary source, all 6 cities searched
- ✅ Realtor.com — Vancouver WA searched (redirected from Zillow)
- ⚠️ Redfin, Auction.com, Hubzu, Xome, HUD Home Store, Foreclosure.com — Browser relay issues prevented full searches; these sources typically have fewer listings in this area/price range

*Report generated March 21, 2026*
"""

print(report)

with open('home_listings_report.md', 'w') as f:
    f.write(report)
print('Report saved to home_listings_report.md')
