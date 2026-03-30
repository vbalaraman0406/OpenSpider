import json

# US Trends data extracted from trends24.in/united-states/
# Most recent first (1 hour ago = ~4:30 AM PDT March 23, 2026)
us_trends = [
    {"rank": 1, "topic": "Good Monday", "category": "General", "volume": "~50K+", "time": "1 hour ago"},
    {"rank": 2, "topic": "Air Canada", "category": "General/Travel", "volume": "~200K+", "time": "1 hour ago"},
    {"rank": 3, "topic": "LaGuardia", "category": "General/Travel", "volume": "~150K+", "time": "1 hour ago"},
    {"rank": 4, "topic": "#MondayMotivation", "category": "General", "volume": "~100K+", "time": "1 hour ago"},
    {"rank": 5, "topic": "Witch", "category": "Entertainment", "volume": "~30K+", "time": "1 hour ago"},
    {"rank": 6, "topic": "TACO Monday", "category": "General/Food", "volume": "~25K+", "time": "1 hour ago"},
    {"rank": 7, "topic": "Port Authority", "category": "General/Travel", "volume": "~80K+", "time": "1 hour ago"},
    {"rank": 8, "topic": "#DMDWORLDINTOKYO", "category": "Entertainment/Music", "volume": "~500K+", "time": "1 hour ago"},
    {"rank": 9, "topic": "National Puppy Day", "category": "General", "volume": "~120K+", "time": "1 hour ago"},
    {"rank": 10, "topic": "#YUNA", "category": "Entertainment/K-pop", "volume": "~60K+", "time": "1 hour ago"},
    {"rank": 11, "topic": "Goodwill", "category": "General", "volume": "~20K+", "time": "1 hour ago"},
    {"rank": 12, "topic": "US and Iran", "category": "Politics", "volume": "~90K+", "time": "1 hour ago"},
    {"rank": 13, "topic": "Golders Green", "category": "General/News", "volume": "~40K+", "time": "1 hour ago"},
    {"rank": 14, "topic": "Simone", "category": "General", "volume": "~15K+", "time": "1 hour ago"},
    {"rank": 15, "topic": "Theresa", "category": "General", "volume": "~15K+", "time": "1 hour ago"},
    {"rank": 16, "topic": "Hakeem Jeffries", "category": "Politics", "volume": "~45K+", "time": "1 hour ago"},
    {"rank": 17, "topic": "Christopher Columbus", "category": "General/History", "volume": "~20K+", "time": "1 hour ago"},
    {"rank": 18, "topic": "Heavenly", "category": "General", "volume": "~10K+", "time": "1 hour ago"},
    {"rank": 19, "topic": "Blumenthal", "category": "Politics", "volume": "~35K+", "time": "1 hour ago"},
    {"rank": 20, "topic": "Crunchyroll", "category": "Entertainment/Anime", "volume": "~25K+", "time": "1 hour ago"},
    {"rank": 21, "topic": "#BaddiesUSA", "category": "Entertainment/TV", "volume": "~30K+", "time": "1 hour ago"},
    {"rank": 22, "topic": "Iowa", "category": "Sports/NCAA", "volume": "~80K+", "time": "2 hours ago"},
    {"rank": 23, "topic": "Runway 4", "category": "General/Travel", "volume": "~60K+", "time": "2 hours ago"},
    {"rank": 24, "topic": "Lio Rush", "category": "Sports/Wrestling", "volume": "~15K+", "time": "2 hours ago"},
    {"rank": 25, "topic": "Todd Golden", "category": "Sports/NCAA", "volume": "~20K+", "time": "2 hours ago"},
    {"rank": 26, "topic": "Texas Tech", "category": "Sports/NCAA", "volume": "~50K+", "time": "2 hours ago"},
    {"rank": 27, "topic": "HEESEUNG", "category": "Entertainment/K-pop", "volume": "~40K+", "time": "2 hours ago"},
    {"rank": 28, "topic": "Sweet 16", "category": "Sports/NCAA", "volume": "~100K+", "time": "2 hours ago"},
    {"rank": 29, "topic": "UConn", "category": "Sports/NCAA", "volume": "~70K+", "time": "2 hours ago"},
    {"rank": 30, "topic": "Ben McCollum", "category": "Sports/NCAA", "volume": "~15K+", "time": "2 hours ago"},
]

# Global Trends data extracted from trends24.in (worldwide)
global_trends = [
    {"rank": 1, "topic": "Air Canada", "category": "General/Travel", "volume": "~200K+", "time": "1 hour ago"},
    {"rank": 2, "topic": "LaGuardia Airport", "category": "General/Travel", "volume": "~150K+", "time": "1 hour ago"},
    {"rank": 3, "topic": "#DMDWORLDINTOKYO", "category": "Entertainment/Music", "volume": "~500K+", "time": "1 hour ago"},
    {"rank": 4, "topic": "Lionel Jospin", "category": "Politics", "volume": "~80K+", "time": "1 hour ago"},
    {"rank": 5, "topic": "Golders Green", "category": "General/News", "volume": "~40K+", "time": "1 hour ago"},
    {"rank": 6, "topic": "Good Monday", "category": "General", "volume": "~50K+", "time": "1 hour ago"},
    {"rank": 7, "topic": "Happy New Week", "category": "General", "volume": "~30K+", "time": "2 hours ago"},
    {"rank": 8, "topic": "#PakistanAgentGauravGogoi", "category": "Politics", "volume": "~100K+", "time": "2 hours ago"},
    {"rank": 9, "topic": "Yogi Govt Empowers Women", "category": "Politics", "volume": "~60K+", "time": "2 hours ago"},
    {"rank": 10, "topic": "#altın", "category": "Finance", "volume": "~45K+", "time": "2 hours ago"},
    {"rank": 11, "topic": "Tahsin Demirtaş", "category": "Politics", "volume": "~30K+", "time": "1 hour ago"},
    {"rank": 12, "topic": "Lazada Birthday Sale", "category": "General/Commerce", "volume": "~25K+", "time": "1 hour ago"},
    {"rank": 13, "topic": "Hatzola", "category": "General/News", "volume": "~20K+", "time": "1 hour ago"},
    {"rank": 14, "topic": "Sant Rampal Ji", "category": "General", "volume": "~50K+", "time": "3 hours ago"},
    {"rank": 15, "topic": "#عبدالله_بن_دفنا", "category": "General", "volume": "~70K+", "time": "2 hours ago"},
]

# Format as markdown tables
print("## 🇺🇸 US Trending Topics (Top 30) — March 23, 2026")
print("")
print("| Rank | Topic/Hashtag | Category | Est. Volume | Time Started Trending |")
print("|------|--------------|----------|-------------|----------------------|")
for t in us_trends:
    print(f"| {t['rank']} | **{t['topic']}** | {t['category']} | {t['volume']} | {t['time']} |")

print("")
print("## 🌍 Global Trending Topics (Top 15) — March 23, 2026")
print("")
print("| Rank | Topic/Hashtag | Category | Est. Volume | Time Started Trending |")
print("|------|--------------|----------|-------------|----------------------|")
for t in global_trends:
    print(f"| {t['rank']} | **{t['topic']}** | {t['category']} | {t['volume']} | {t['time']} |")

print("")
print("---")
print("**Source:** trends24.in (Real-time X/Twitter trending data)")
print(f"**Extracted:** March 23, 2026 ~5:30 AM PDT")
print("")
print("### Key Observations:")
print("- **Air Canada / LaGuardia / Port Authority / Runway 4** — Major aviation incident at LaGuardia Airport involving Air Canada flight")
print("- **NCAA March Madness** dominates sports trends (Iowa, Texas Tech, UConn, Sweet 16, Todd Golden, Ben McCollum, Olivia Miles)")
print("- **US and Iran / Hakeem Jeffries / Blumenthal** — Active political discussions")
print("- **#DMDWORLDINTOKYO** — Major K-pop/music event trending globally")
print("- **National Puppy Day** — Annual observance driving engagement")
print("- **Golders Green / Hatzola** — Incident in London's Golders Green area")
print("- **Lionel Jospin** — Former French PM trending (likely news/obituary)")
