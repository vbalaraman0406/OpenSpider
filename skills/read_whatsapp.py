with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    lines = f.readlines()

# Find the send_whatsapp block
start = None
for i, line in enumerate(lines):
    if "send_whatsapp" in line and "response.action" in line:
        start = i
        break

if start:
    # Print from start to ~120 lines after
    for i in range(start, min(start + 120, len(lines))):
        print(f"{i+1}: {lines[i]}", end='')
