with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

# Print lines 338-410 in two chunks to avoid truncation
for i in range(337, min(375, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
