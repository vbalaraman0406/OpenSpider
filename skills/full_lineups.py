import requests
from bs4 import BeautifulSoup
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
r = requests.get('https://www.rotowire.com/baseball/daily-lineups.php', headers=headers, timeout=15)
soup = BeautifulSoup(r.text, 'html.parser')
boxes = soup.select('div.lineup__box')

all_games = []
for box in boxes:
    teams = [t.get_text(strip=True) for t in box.select('.lineup__abbr')]
    full = [t.get_text(strip=True) for t in box.select('.lineup__mteam')]
    status = box.select_one('.lineup__status')
    status_t = status.get_text(strip=True) if status else 'Unknown'
    
    pitchers = box.select('.lineup__player-highlight-name')
    sp = [p.get_text(strip=True) for p in pitchers]
    
    lists = box.select('.lineup__list')
    lineups = [[], []]
    for li, ll in enumerate(lists[:2]):
        for p in ll.select('.lineup__player'):
            pos_el = p.select_one('.lineup__pos')
            pos = pos_el.get_text(strip=True) if pos_el else ''
            a = p.select_one('a')
            name = a.get_text(strip=True) if a else p.get_text(strip=True)
            bats_el = p.select_one('.lineup__bats')
            bats = bats_el.get_text(strip=True) if bats_el else ''
            if bats and name.endswith(bats):
                name = name[:-len(bats)].strip()
            if pos and name.startswith(pos):
                name = name[len(pos):].strip()
            lineups[li].append(f'{pos} {name}'.strip())
    
    away = teams[0] if len(teams) > 0 else 'TBD'
    home = teams[1] if len(teams) > 1 else 'TBD'
    g = f"**{away} @ {home}** | Status: {status_t}\n"
    g += f"SP: {sp[0] if len(sp)>0 else 'TBD'} vs {sp[1] if len(sp)>1 else 'TBD'}\n"
    if lineups[0]:
        g += f"{away}: " + ', '.join(f'{i+1}.{p}' for i,p in enumerate(lineups[0])) + '\n'
    else:
        g += f"{away}: No lineup posted\n"
    if lineups[1]:
        g += f"{home}: " + ', '.join(f'{i+1}.{p}' for i,p in enumerate(lineups[1])) + '\n'
    else:
        g += f"{home}: No lineup posted\n"
    all_games.append(g)

print(f'=== {datetime.now().strftime("%Y-%m-%d")} MLB Lineups ({len(boxes)} games) ===')
for g in all_games:
    print(g)
