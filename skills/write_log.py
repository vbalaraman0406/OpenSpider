import os
workspace = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workspace')
os.makedirs(workspace, exist_ok=True)
log_path = os.path.join(workspace, 'f1_fantasy_log.md')
content = '''# F1 Fantasy Weekly Log

| Date | Status | Notes |
|---|---|---|
| 2026-03-05 | No upcoming race this week | Next race: 🇦🇺 Australian GP (Round 1) — FP1: Mar 13, Race: Mar 15 |
'''
# Append if exists, otherwise create
mode = 'a' if os.path.exists(log_path) else 'w'
with open(log_path, mode) as f:
    if mode == 'a':
        f.write('| 2026-03-05 | No upcoming race this week | Next race: 🇦🇺 Australian GP (Round 1) — FP1: Mar 13, Race: Mar 15 |\n')
    else:
        f.write(content)
print(f'Log written to {log_path}')
with open(log_path) as f:
    print(f.read())
