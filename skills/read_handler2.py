with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

for i in range(374, min(420, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
