with open('weather_output.md', 'r') as f:
    content = f.read()

# Print in sections to avoid truncation
lines = content.split('\n')
for i, line in enumerate(lines):
    print(f'{i}: {line}')
