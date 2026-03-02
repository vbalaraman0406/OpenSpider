import urllib.request
import json

repos = [
    ('moeru-ai/airi', 'TypeScript', '736', 'Self hosted, you-owned Grok Companion, a container of souls of waifu, cyber livings to bring them into our worlds. Capable of realtime voice chat, Minecraft, Factorio playing.'),
    ('ruvnet/wifi-densepose', 'Rust', '4,539', 'WiFi DensePose turns commodity WiFi signals into real-time human pose estimation, vital sign monitoring, and presence detection without video.'),
    ('ruvnet/ruflo', 'TypeScript', '766', 'The leading agent orchestration platform for Claude. Deploy intelligent multi-agent swarms, coordinate autonomous workflows, and build conversational AI systems.'),
    ('microsoft/markitdown', 'Python', '805', 'Python tool for converting files and office documents to Markdown.'),
    ('bytedance/deer-flow', 'Python', '355', 'An open-source SuperAgent harness that researches, codes, and creates with sandboxes, memories, tools, skills and subagents.')
]

for i, (repo, lang, stars_today, desc) in enumerate(repos, 1):
    try:
        url = f'https://api.github.com/repos/{repo}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode('utf-8'))
        total_stars = f"{data['stargazers_count']:,}"
        forks = f"{data['forks_count']:,}"
    except Exception as e:
        total_stars = 'N/A'
        forks = 'N/A'
    print(f"RANK:{i}|NAME:{repo}|LANG:{lang}|STARS_TODAY:{stars_today}|TOTAL:{total_stars}|FORKS:{forks}|DESC:{desc}")
