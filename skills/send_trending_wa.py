import os, sys
sys.path.insert(0, '/Users/vbalaraman/OpenSpider/skills')

try:
    from whatsapp_messaging import send_message
    msg = ("TRENDING NOW - Top 10 X Twitter Trends (March 28, 2026)\n\n"
           "1. IranWar - Israel intensifies strikes, Strait of Hormuz locked down, oil past 110 per barrel. Trump extends deadline to April 6.\n"
           "2. Stock Market CRASH - Dow enters correction (-793pts), SP500 5th straight losing week, Nasdaq confirms correction.\n"
           "3. Tiger Woods DUI - Arrested after rollover crash in Jupiter Island FL. Released on bail before Masters.\n"
           "4. NoKings Protests - 3000+ protests across US today against Trump. Biggest day of protest yet.\n"
           "5. Elon Musk Loses Trial - Jury finds Musk liable for defrauding Twitter shareholders. 2.5B potential damages.\n"
           "6. AI Safety Crisis - Anthropic Claude AI clashes with Pentagon, sycophancy study shows chatbots give dangerous advice.\n"
           "7. Magnificent 7 Meltdown - Tech giants shed 300B in single day. Worst tech week in a year.\n"
           "8. Government Shutdown - Partial shutdown continues amid war and protests.\n"
           "9. Earth Hour 2026 - Global lights-out event tonight March 28.\n"
           "10. China Trade Probes - Beijing opens investigations into US trade practices in retaliation.\n\n"
           "Source: Reuters, Bloomberg, CNBC, BBC, NYT, Reddit, X Trending")
    
    targets = ["14156249639@s.whatsapp.net", "16507965072@s.whatsapp.net"]
    for t in targets:
        try:
            result = send_message(t, msg)
            print(f"Sent to {t}: {result}")
        except Exception as e:
            print(f"Error sending to {t}: {e}")
except ImportError as e:
    print(f"Import error: {e}")
    # Try direct execution
    print("Trying direct file read to find the right approach...")
    with open('/Users/vbalaraman/OpenSpider/skills/whatsapp_messaging.py', 'r') as f:
        content = f.read()[:2000]
    print(content)
