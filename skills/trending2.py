import urllib.request
import re

url = 'https://github.com/trending'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req)
html = resp.read().decode('utf-8')

article_splits = html.split('<article class="Box-row"')
for i, block in enumerate(article_splits[1:6], 1):
    m = re.search(r'<h2[^>]*>\s*<a[^>]*href="(/[^"]+)"', block)
    repo_path = m.group(1).strip() if m else ''
    repo_name = repo_path.lstrip('/')
    repo_url = 'https://github.com' + repo_path if repo_path else ''
    
    m_desc = re.search(r'<p class="col-9[^"]*"[^>]*>([^<]+)</p>', block)
    desc = m_desc.group(1).strip() if m_desc else 'N/A'
    
    m_lang = re.search(r'<span itemprop="programmingLanguage">([^<]+)</span>', block)
    lang = m_lang.group(1).strip() if m_lang else 'N/A'
    
    # Find all links with counts - stars and forks are in <a> tags with href ending in /stargazers and /network/members
    star_match = re.search(r'href="' + re.escape(repo_path) + r'/stargazers"[^>]*>\s*([\d,]+)\s*</a>', block)
    total_stars = star_match.group(1).strip() if star_match else 'N/A'
    
    fork_match = re.search(r'href="' + re.escape(repo_path) + r'/forks"[^>]*>\s*([\d,]+)\s*</a>', block)
    if not fork_match:
        fork_match = re.search(r'href="' + re.escape(repo_path) + r'/network/members"[^>]*>\s*([\d,]+)\s*</a>', block)
    forks = fork_match.group(1).strip() if fork_match else 'N/A'
    
    # If still N/A, try broader patterns
    if total_stars == 'N/A':
        all_nums = re.findall(r'<a[^>]*href="[^"]*stargazers[^"]*"[^>]*>\s*([\d,]+)', block)
        total_stars = all_nums[0].strip() if all_nums else 'N/A'
    if forks == 'N/A':
        all_forks = re.findall(r'<a[^>]*href="[^"]*(?:forks|network/members)[^"]*"[^>]*>\s*([\d,]+)', block)
        forks = all_forks[0].strip() if all_forks else 'N/A'
    
    m_today = re.search(r'([\d,]+)\s*stars\s*today', block)
    stars_today = m_today.group(1).strip() if m_today else 'N/A'
    
    print(f"RANK:{i}|NAME:{repo_name}|URL:{repo_url}|LANG:{lang}|STARS_TODAY:{stars_today}|TOTAL:{total_stars}|FORKS:{forks}|DESC:{desc}")
