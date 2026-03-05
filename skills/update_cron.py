import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

# Update existing jobs
for job in jobs:
    if job['name'] == 'Daily S&P 500 & NASDAQ Market Snapshot':
        job['whatsappGroup'] = 'Stock Market Discussions'
        job['prompt'] = (
            "Fetch the latest S&P 500 and NASDAQ market data and send a Daily S&P 500 & NASDAQ Market Snapshot email to ALL: "
            "coolvishnu@gmail.com, cskums@gmail.com, singhsatish77@gmail.com, pratheepkr@gmail.com, sornakums@gmail.com, shawnholdings@gmail.com. "
            "Include closing prices, daily change, %, volume, top gainers, top losers, sector performance, full market summary. "
            "Mon-Fri only, skip weekends & US holidays. "
            "ALSO send the same market snapshot content as a WhatsApp message to the group 'Stock Market Discussions' using the send_whatsapp tool."
        )
    elif job['name'] == 'Pre-Market Morning Brief - S&P 500 & NASDAQ':
        job['whatsappGroup'] = 'Stock Market Discussions'
        job['prompt'] = (
            "Fetch latest S&P 500 and NASDAQ pre-market data including futures, overnight global market performance, "
            "key economic events for the day, and market outlook. Send email to ALL: coolvishnu@gmail.com, cskums@gmail.com, "
            "singhsatish77@gmail.com, pratheepkr@gmail.com, sornakums@gmail.com, shawnholdings@gmail.com. "
            "Mon-Fri only, skip weekends & US holidays. "
            "ALSO send the same pre-market brief content as a WhatsApp message to the group 'Stock Market Discussions' using the send_whatsapp tool."
        )

# Add new Iran War Update job
iran_job = {
    "name": "Iran War Update",
    "intervalHours": 24,
    "preferredTime": "06:00",
    "prompt": (
        "Search the web for the latest news and developments on the Iran war / US-Iran conflict. "
        "Compile a comprehensive update covering military operations, diplomatic developments, regional escalation, "
        "economic/market impact, and humanitarian situation. "
        "Send this update as a WhatsApp message to the group 'Stock Market Discussions' using the send_whatsapp tool."
    ),
    "whatsappGroup": "Stock Market Discussions",
    "enabled": True,
    "lastRun": None
}
jobs.append(iran_job)

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print(f'Updated cron_jobs.json — {len(jobs)} total jobs')
for j in jobs:
    wg = j.get('whatsappGroup', 'N/A')
    print(f"  - {j['name']} | preferredTime={j.get('preferredTime','N/A')} | whatsappGroup={wg}")
