with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

# Print lines 372-392
for i in range(372, min(392, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
