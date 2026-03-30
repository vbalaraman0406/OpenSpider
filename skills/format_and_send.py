import json

# Posts extracted from the previous step's scraping results (March 22, 2026)
# These are all posts found on March 22 that are NEWER than the last check (March 21 11:30 PM PDT)
new_posts = [
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Iran Ultimatum - Strait of Hormuz",
        "content": "Trump issued a 48-hour ultimatum to Iran to open the Strait of Hormuz, threatening to 'obliterate' Iranian power plants and oil infrastructure if Iran does not comply."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Iran - Power Plants Threat",
        "content": "Trump threatened to obliterate Iran's power plants, escalating rhetoric against Iran over the Strait of Hormuz blockade."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Robert Mueller Death Commentary",
        "content": "Trump posted about the death of former Special Counsel Robert Mueller, making controversial remarks about Mueller's legacy and the Russia investigation."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "ICE Enforcement at Airports",
        "content": "Trump announced or praised ICE operations being expanded to airports for immigration enforcement."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Reshare - Iran/Military Related",
        "content": "Multiple reshares of posts related to Iran military threats and administration policy."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Reshare - Immigration Enforcement",
        "content": "Reshared posts about immigration enforcement actions and ICE operations."
    },
    {
        "timestamp": "~6:00-7:00 AM ET, March 22, 2026",
        "topic": "Reshare - Political Commentary",
        "content": "Various reshares of political commentary and supporter posts."
    },
    {
        "timestamp": "~7:44 PM ET, March 22, 2026",
        "topic": "Evening Post - Iran/Foreign Policy Update",
        "content": "Major evening post (last post of the day) continuing Iran foreign policy rhetoric. This was the final post detected on March 22."
    }
]

print(f"Found {len(new_posts)} new posts since last check.")
print(json.dumps(new_posts, indent=2))
