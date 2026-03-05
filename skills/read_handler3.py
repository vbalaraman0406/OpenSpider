with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

for i in range(382, min(410, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')
