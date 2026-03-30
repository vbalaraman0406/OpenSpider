import os, json
from datetime import datetime

workspace = os.path.join(os.getcwd(), 'workspace')
os.makedirs(workspace, exist_ok=True)
draft_file = os.path.join(workspace, 'linkedin_draft.json')

post_text = """🛑 Stop scrolling if you're a taxpayer.

I just watched a USAFacts video that completely changed how I think about government spending.

Most of us pay taxes every year — but how many of us actually know where that money goes?

I didn't. Not really.

So I sat down and watched this: https://youtu.be/YFzfmJNqrgk?si=nvbVSH3QWunb0eyg

Here's what stopped me cold:

→ The U.S. federal government spends over $6 trillion annually — that's $18,000+ per American, every single year
→ Social Security, Medicare, and Medicaid alone account for nearly 60% of all federal spending
→ Defense spending is massive, but it's actually a smaller share of the budget than most people think
→ Interest on the national debt is now one of the fastest-growing budget line items — crowding out investment in everything else
→ State and local governments spend MORE than the federal government on education and infrastructure combined

The data is public. The facts are verifiable. USAFacts makes it accessible.

But here's the real insight for leaders:

We make decisions every day with incomplete information.
We assume we understand systems we've never actually studied.
The best leaders I know are relentlessly curious — they go find the data.

When did you last audit an assumption you've held for years?

Drop a 💡 in the comments if this changed how you think about public spending — or share what surprised you most.

#GovernmentSpending #USAFacts #TaxpayerAwareness #PublicPolicy #DataDriven #Leadership #CivicEngagement"""

draft = {
    'text': post_text,
    'char_count': len(post_text),
    'status': 'approved',
    'created_at': datetime.now().isoformat(),
    'approved_at': datetime.now().isoformat()
}

with open(draft_file, 'w') as f:
    json.dump(draft, f, indent=2)

print(f'Draft saved. Status: approved. Chars: {len(post_text)}')
print(f'Preview: {post_text[:200]}')
