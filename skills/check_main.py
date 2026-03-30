with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    print(f'{i}: {line}', end='')
