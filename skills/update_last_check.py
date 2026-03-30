import os

os.makedirs('workspace/memory', exist_ok=True)

content = """# Trump Truth Social - Last Check

## Last Check Time
Saturday, March 21, 2026 at 3:03 PM PDT

## Last Known Posts (as of this check)
1. Mar-a-Lago Throwback Photo (~1:01 PM PDT March 21, 2026)
   Content: In the early days of Mar-a-Lago! (accompanied by a photo)

2. Robert Mueller Death Post (~12:12-12:25 PM PDT March 21, 2026)
   Content: Robert Mueller just died. Good, I'm glad he's dead. He can no longer hurt innocent people!

3. ICE Agents at Airports (~8:45 AM PDT March 21, 2026)
   Content: If the Democrats do not allow for Just and Proper Security at our Airports...ICE will do the job far better than ever done before!

4. Iran Military Operations (Pinned post, ~March 20, 2026)
   Content: Today Iran will be hit very hard! and related posts about Strait of Hormuz, South Pars gas field strikes

## Status
No new posts within the 30-min window (2:33-3:03 PM PDT). Added Mar-a-Lago throwback post (~1:01 PM) to known posts list - it was present on the page but not in previous check's catalog. No WhatsApp alert sent.
"""

with open('workspace/memory/trump_truth_last_check.md', 'w') as f:
    f.write(content)

print('Last check file updated successfully.')
