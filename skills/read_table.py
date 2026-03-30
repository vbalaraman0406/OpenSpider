with open('weather_output.md', 'r') as f:
    lines = f.readlines()

# Print just the table rows (lines 12-25)
for i in range(12, min(25, len(lines))):
    print(lines[i].rstrip())
