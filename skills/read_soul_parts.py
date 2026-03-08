with open('/Users/vbalaraman/OpenSpider/workspace/agents/manager/SOUL.md', 'r') as f:
    content = f.read()
print('=== PART 1 (0-1000) ===')
print(content[:1000])
print('=== PART 3 (2500-end) ===')
print(content[2500:])