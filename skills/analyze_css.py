import re

with open('/Users/vbalaraman/OpenSpider/f1_theme.css', 'r') as f:
    css = f.read()

print(f'CSS file size: {len(css)} bytes')

# Search for color-related patterns
colors = re.findall(r'#[0-9a-fA-F]{3,8}', css)
print(f'Total color values found: {len(colors)}')

# Count occurrences
from collections import Counter
color_counts = Counter([c.lower() for c in colors])
print('\nTop 30 colors:')
for color, count in color_counts.most_common(30):
    print(f'  {color}: {count}')

# Check specific theme indicators
print('\n--- Theme Analysis ---')
dark_bg = [c for c, n in color_counts.items() if c in ['#0f0f1b', '#1a1a2e', '#16213e', '#0a0a0a', '#111', '#000', '#111111', '#0d1117', '#1e1e2e']]
print(f'Dark background colors: {dark_bg}')

red_accent = [c for c, n in color_counts.items() if c.startswith('#e1') or c.startswith('#ff1') or c.startswith('#dc') or c.startswith('#ef4') or c.startswith('#b91')]
print(f'Red accent colors: {red_accent}')

white_text = [c for c, n in color_counts.items() if c in ['#fff', '#ffffff', '#f5f5f5', '#e5e5e5', '#fafafa', '#f0f0f0']]
print(f'White/light text colors: {white_text}')

# Check for pitwall custom classes
pitwall_refs = re.findall(r'pitwall[\w-]*', css)
print(f'\nPitwall class references: {list(set(pitwall_refs))[:20]}')

# Check for Tailwind dark classes
if 'dark' in css.lower():
    print('Dark mode references found in CSS')
