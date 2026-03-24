import json

# Based on the parallel search results, here are the listings found:
# Redfin found 5 listings, Realtor.com found similar listings
# Auction/foreclosure sites found 0
# Zillow was incomplete

listings = [
    {
        "address": "6610 NE 106th Cir, Vancouver, WA 98686",
        "price": "Contact for price",
        "price_num": 0,
        "beds": 5,
        "baths": 2.5,
        "sqft": "N/A",
        "year_built": "2017+",
        "source": "Redfin / Realtor.com",
        "link": "https://www.redfin.com/WA/Vancouver/6610-NE-106th-Cir-98686/home/168211412"
    },
    {
        "address": "915 NE 146th St, Vancouver, WA 98685",
        "price": "Contact for price",
        "price_num": 0,
        "beds": 5,
        "baths": 2.5,
        "sqft": "N/A",
        "year_built": "2017+",
        "source": "Redfin / Realtor.com",
        "link": "https://www.redfin.com/WA/Vancouver/915-NE-146th-St-98685/home/14603847"
    },
    {
        "address": "12500 NE 107th Way, Vancouver, WA 98682",
        "price": "Contact for price",
        "price_num": 0,
        "beds": 5,
        "baths": 2.5,
        "sqft": "N/A",
        "year_built": "2017+",
        "source": "Redfin / Realtor.com",
        "link": "https://www.redfin.com/WA/Vancouver/12500-NE-107th-Way-98682/home/144770473"
    },
    {
        "address": "6901 NE 16th Ave, Vancouver, WA 98665",
        "price": "Contact for price",
        "price_num": 0,
        "beds": 5,
        "baths": 2.5,
        "sqft": "N/A",
        "year_built": "2017+",
        "source": "Redfin / Realtor.com",
        "link": "https://www.redfin.com/WA/Vancouver/6901-NE-16th-Ave-98665/home/175015284"
    },
    {
        "address": "18711 NE 41st Pl #319, Vancouver, WA 98686",
        "price": "Contact for price",
        "price_num": 0,
        "beds": 5,
        "baths": 2.5,
        "sqft": "N/A",
        "year_built": "2017+",
        "source": "Redfin / Realtor.com",
        "link": "https://www.redfin.com/WA/Unknown/18711-NE-41st-Pl-98686/unit-319/home/200225257"
    }
]

print(f"Total listings compiled: {len(listings)}")
print("All from Redfin/Realtor.com (deduplicated). Zillow incomplete, Auction sites 0 results.")
