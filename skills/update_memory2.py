import os

base = '/Users/vbalaraman/OpenSpider'
dir_path = os.path.join(base, 'workspace', 'memory')
os.makedirs(dir_path, exist_ok=True)

file_path = os.path.join(dir_path, 'trump_truth_last_check.md')

with open(file_path, 'w') as f:
    f.write('Last check timestamp: 2026-03-20 23:55:00 PDT\n')
    f.write('Last post timestamp: ~2026-03-20 14:47:00 PDT\n')
    f.write('Last post content hash: iran_war_winding_down\n')
    f.write('Last post summary: Most recent post was from ~2:47 PM PDT about winding down the Iran war. No new posts detected. Checked at 11:55 PM PDT.\n')

print(f'Written to {file_path}')
