import os

memory_dir = '/Users/vbalaraman/OpenSpider/workspace/memory'
os.makedirs(memory_dir, exist_ok=True)

content = """# Trump Truth Social - Last Check

## Check Timestamp
- **Last Checked:** 2026-03-21 05:18 AM PDT
- **Status:** SUCCESS - Page loaded via Truth Social directly
- **New Posts Found:** NO

## Latest Known Posts

### Post 1 (Most Recent)
- **Approximate Time:** ~2:18 PM PDT, March 20, 2026 (showed as 15h ago at check time)
- **Topic:** Winding down military efforts in Middle East / Iran
- **Content:** We are getting very close to meeting our objectives as we consider winding down our great Military efforts in the Middle East with respect to the Terrorist Regime of Iran: (1) Completely degrading Iranian Missile Capability, Launchers, and everything else pertaining to them. (2) Destroying Iran's Defense Industrial Base. (3) Eliminating their Navy and Air Force, including Anti Aircraft Weaponry. (4) Never allowing Iran to get even close to Nuclear Capability, and always being in a position where the U.S.A. can quickly and powerfully react to such a situation, should it take place. (5) Protecting, at the highest level, our Middle Eastern Allies, including Israel, Saudi Arabia, Qatar, the United Arab Emirates, Bahrain, Kuwait, and others. The Hormuz Strait will have to be guarded and policed, as necessary, by other Nations who use it - The United States does not! If asked, we will help these Countries in their Hormuz efforts, but it shouldn't be necessary once Iran's threat is eradicated. Importantly, it will be an easy Military Operation for them. Thank you for your attention to this matter! President DONALD J. TRUMP
- **Engagement:** 5.38k replies, 9.73k reTruths, 40.5k likes

### Post 2
- **Approximate Time:** ~3:18 PM PDT, March 20, 2026 (showed as 14h ago at check time)
- **Topic:** Tina Peters / Colorado / Election integrity
- **Content:** The Great State of Colorado, and a pathetic RINO District Attorney, together with the Radical Left Governor, gave a wonderful woman named Tina Peters, a 73-year-old Gold Star Mom, who has cancer, nine years in prison because, as a Republican Voting Official, she went after the Democrats for cheating in the 2020 Presidential Election. So, she went after them for cheating, and these SLEAZEBAGS put her in jail. FREE TINA! President DJT
- **Engagement:** 3.18k replies, 8.14k reTruths, 24.6k likes
"""

with open(os.path.join(memory_dir, 'trump_truth_last_check.md'), 'w') as f:
    f.write(content)

print('Memory file saved successfully.')
