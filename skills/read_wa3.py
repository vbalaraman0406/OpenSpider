with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

# Print lines 349-408 (the truncated middle section)
for i in range(348, min(408, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
