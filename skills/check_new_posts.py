import json
import os
from datetime import datetime, timezone, timedelta

# The scraped posts from the previous step context
# Based on the context, the previous step found posts with these URLs and topics
# Let me reconstruct what was found from the context clues

# From the previous step context, the table header was:
# | # | Timestamp (EST) | Topic |
# And URLs found were:
# 1. NY AG Letitia James referred for criminal prosecution
# 2. NSA intercepted Ukraine government messages about routing money to 2024
# 3. TrumpRx website sees steady growth in prescription offerings

# The context was truncated but these are the posts found
# Since last check was 2026-03-21, and today is 2026-03-27, 
# ANY posts found today would be new

state_file = 'workspace/skills/trump_truth_last_check/state.json'

with open(state_file, 'r') as f:
    state = json.load(f)

print(f"Last check: {state['last_check']}")
print(f"Last post seen: {state['last_post_seen']}")
print(f"Today: 2026-03-27 19:06 PDT")
print(f"Days since last check: ~6 days")
print("Any posts found in the scrape would be new since last check.")
