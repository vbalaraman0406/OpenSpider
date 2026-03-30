from html.parser import HTMLParser

# Extract tweet volumes from trends24.in HTML
with open('/tmp/trends24.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Look for volume/count data near trend names
# trends24.in typically shows volumes like "10K", "50K" etc.
# Let's search for patterns in the raw HTML

# Find all text content between tags
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.current_tag = ''
        self.current_class = ''
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        self.current_class = attrs_dict.get('class', '')
        
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.texts.append((self.current_tag, self.current_class, text))

parser = TextExtractor()
parser.feed(html)

# Look for volume indicators (numbers with K, M, or just numbers near trend names)
trend_data = []
current_trend = None

for tag, cls, text in parser.texts:
    # Check if this looks like a volume number
    if 'K' in text and len(text) < 10:
        if current_trend:
            trend_data.append((current_trend, text))
            current_trend = None
    elif text.startswith('#') or (len(text) > 2 and len(text) < 50 and tag == 'a'):
        current_trend = text

print('Trends with volumes:')
for t, v in trend_data[:50]:
    print(f'  {t}: {v}')

# Also look for specific class names that might contain volume
print('\n--- Looking for volume-related classes ---')
volume_classes = set()
for tag, cls, text in parser.texts:
    if cls and ('vol' in cls.lower() or 'count' in cls.lower() or 'num' in cls.lower() or 'tweet' in cls.lower()):
        print(f'  [{cls}] {text}')
        volume_classes.add(cls)

# Search raw HTML for volume patterns
print('\n--- Searching raw HTML for volume patterns ---')
import html as html_module

# Look for spans/divs with tweet counts
lines = html.split('\n')
for line in lines:
    line_lower = line.lower()
    if ('tweet' in line_lower and ('k' in line_lower or 'volume' in line_lower)) or 'data-count' in line_lower:
        clean = line.strip()[:150]
        if clean:
            print(f'  {clean}')

# Also check getdaytrends for volumes
print('\n=== GETDAYTRENDS VOLUMES ===')
with open('/tmp/getdaytrends.html', 'r', encoding='utf-8', errors='ignore') as f:
    html2 = f.read()

parser2 = TextExtractor()
parser2.feed(html2)

for tag, cls, text in parser2.texts:
    if cls and ('vol' in cls.lower() or 'count' in cls.lower() or 'num' in cls.lower() or 'tweet' in cls.lower() or 'post' in cls.lower()):
        print(f'  [{cls}] {text}')

# Look for table rows with numbers
print('\n--- Table data with numbers ---')
for i, (tag, cls, text) in enumerate(parser2.texts):
    if tag == 'td' or tag == 'span':
        if any(c.isdigit() for c in text) and len(text) < 20:
            # Get surrounding context
            context = ''
            for j in range(max(0, i-3), min(len(parser2.texts), i+3)):
                context += parser2.texts[j][2] + ' | '
            print(f'  {text} -> context: {context[:120]}')
