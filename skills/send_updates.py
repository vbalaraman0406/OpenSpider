with open('workspace/f1_fantasy_update.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('workspace/f1_fantasy_update_wa.txt', 'r', encoding='utf-8') as f:
    wa = f.read()
print('HTML_LENGTH:', len(html))
print('WA_LENGTH:', len(wa))
print('---HTML_START---')
print(html[:500])
print('---WA_START---')
print(wa[:500])