import urllib.request
from html.parser import HTMLParser
import re

url = 'https://github.com/trending'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req)
html = resp.read().decode('utf-8')

# Extract repo articles
repos = []
# Find all article blocks for repos
article_splits = html.split('<article class="Box-row"')
for i, block in enumerate(article_splits[1:6], 1):  # top 5
    # Repo name (owner/repo)
    m = re.search(r'<h2[^>]*>\s*<a[^>]*href="(/[^"]+)"', block)
    repo_path = m.group(1).strip() if m else ''
    repo_name = repo_path.lstrip('/')
    repo_url = 'https://github.com' + repo_path if repo_path else ''
    
    # Description
    m_desc = re.search(r'<p class="col-9[^"]*"[^>]*>([^<]+)</p>', block)
    desc = m_desc.group(1).strip() if m_desc else 'N/A'
    
    # Language
    m_lang = re.search(r'<span itemprop="programmingLanguage">([^<]+)</span>', block)
    lang = m_lang.group(1).strip() if m_lang else 'N/A'
    
    # Total stars - look for SVG with octicon-star followed by a number
    star_matches = re.findall(r'octicon-star[^>]*>[^<]*</svg>\s*([\d,]+)', block)
    total_stars = star_matches[0].strip() if star_matches else 'N/A'
    
    # Forks
    fork_matches = re.findall(r'octicon-repo-forked[^>]*>[^<]*</svg>\s*([\d,]+)', block)
    forks = fork_matches[0].strip() if fork_matches else 'N/A'
    
    # Stars today
    m_today = re.search(r'([\d,]+)\s*stars\s*today', block)
    stars_today = m_today.group(1).strip() if m_today else 'N/A'
    
    repos.append({
        'rank': i,
        'name': repo_name,
        'url': repo_url,
        'lang': lang,
        'stars_today': stars_today,
        'total_stars': total_stars,
        'forks': forks,
        'desc': desc
    })

for r in repos:
    print(f"RANK:{r['rank']}|NAME:{r['name']}|URL:{r['url']}|LANG:{r['lang']}|STARS_TODAY:{r['stars_today']}|TOTAL_STARS:{r['total_stars']}|FORKS:{r['forks']}|DESC:{r['desc']}")
