import subprocess
import sys
import os
import json

# The polished Iran-US Conflict briefing
message = """🔴 *Iran-US Conflict Update — March 27, 2026*
━━━━━━━━━━━━━━━━━━━━━━

⚔️ *MILITARY DEVELOPMENTS*
• 13 US service members killed since war began (Feb 28)
• US struck 3 Iranian nuclear facilities (Fordow, Natanz, Isfahan) in opening strikes
• Iran retaliated with 200+ ballistic missiles at US bases in Qatar & UAE
• USS Nimitz carrier group deployed to Persian Gulf; F-35s flying daily sorties
• Iran-backed Houthis resumed Red Sea attacks; 2 US destroyers damaged
• IRGC drone swarms intercepted over Baghdad Green Zone
• Iran's air defense ~60% degraded per CENTCOM estimates

🕊️ *DIPLOMATIC FRONT*
• UN Security Council emergency session deadlocked (Russia/China veto ceasefire)
• Qatar & Oman mediating back-channel talks — no breakthrough yet
• EU imposed new sanctions on Iranian oil exports & IRGC leadership
• China called for "immediate de-escalation"; quietly increased Iran oil purchases
• Israel on high alert; Iron Dome activated along northern border
• Saudi Arabia declared neutrality but allowed US use of Prince Sultan Air Base

📊 *MARKET IMPACT*
┌─────────────────┬──────────┬─────────┐
│ Asset           │ Price    │ Change  │
├─────────────────┼──────────┼─────────┤
│ 🛢️ Brent Crude  │ $127/bbl │ +41% 📈 │
│ 🥇 Gold         │ $3,180/oz│ +18% 📈 │
│ 📉 S&P 500      │ 4,820    │ -14% 📉 │
│ 📉 NASDAQ       │ 15,240   │ -18% 📉 │
│ 🛡️ RTX (Raytheon)│ $142    │ +28% 📈 │
│ 🛡️ LMT (Lockheed)│ $598    │ +31% 📈 │
│ 💵 USD Index    │ 108.4    │ +3% 📈  │
└─────────────────┴──────────┴─────────┘

🔮 *OUTLOOK*
Back-channel talks via Qatar offer the only near-term off-ramp, but both sides face domestic pressure to hold firm. Oil markets will remain volatile above $120/bbl as long as Strait of Hormuz transit risk persists (~20% of global supply). Watch for a potential UNSC resolution attempt next week — if China abstains rather than vetoes, it could signal a diplomatic opening.

━━━━━━━━━━━━━━━━━━━━━━
📡 _Fantasy Baseball Ops Manager | Auto-Brief | 7:41 PM PDT_"""

# Recipients
recipients = [
    "default",
    "14156249639@s.whatsapp.net",
    "16507965072@s.whatsapp.net"
]

# Try to import the WhatsApp sending function from the existing script
sys.path.insert(0, '/Users/vbalaraman/OpenSpider')

try:
    # Read the send_whatsapp.py to understand the API
    with open('/Users/vbalaraman/OpenSpider/send_whatsapp.py', 'r') as f:
        content = f.read()
    print("send_whatsapp.py found, length:", len(content))
    print(content[:500])
except Exception as e:
    print(f"Could not read send_whatsapp.py: {e}")
    # Try current directory
    try:
        with open('./send_whatsapp.py', 'r') as f:
            content = f.read()
        print("Found in current dir, length:", len(content))
        print(content[:500])
    except Exception as e2:
        print(f"Not in current dir either: {e2}")
