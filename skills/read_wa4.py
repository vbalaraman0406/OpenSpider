with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

# Print lines 360-401 (the truncated middle)
for i in range(359, min(401, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
