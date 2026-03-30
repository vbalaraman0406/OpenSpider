from html.parser import HTMLParser

class TableExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.in_a = False
        self.current_href = ''
        self.cells = []
        self.current_cell = ''
        self.rows = []
        self.in_tr = False
        self.all_texts = []
        self.current_tag = ''
        self.current_class = ''
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        self.current_class = attrs_dict.get('class', '')
        if tag == 'tr':
            self.in_tr = True
            self.cells = []
        elif tag == 'td':
            self.in_td = True
            self.current_cell = ''
        elif tag == 'a':
            self.in_a = True
            self.current_href = attrs_dict.get('href', '')
            
    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_td = False
            self.cells.append(self.current_cell.strip())
        elif tag == 'tr':
            self.in_tr = False
            if self.cells:
                self.rows.append(self.cells)
        elif tag == 'a':
            self.in_a = False
            
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.all_texts.append((self.current_tag, self.current_class, text))
            if self.in_td:
                self.current_cell += ' ' + text

# Parse getdaytrends.com
with open('/tmp/getdaytrends.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

parser = TableExtractor()
parser.feed(html)

print('=== GETDAYTRENDS.COM - FULL TRENDING LIST ===')
print(f'Total table rows: {len(parser.rows)}')

trending_topics = []
for row in parser.rows:
    # Filter rows that look like trend entries (have a number, name, volume)
    if len(row) >= 2:
        # Check if first cell is a number (rank)
        first = row[0].strip()
        if first.isdigit():
            rank = int(first)
            name = row[1].strip() if len(row) > 1 else ''
            volume = row[2].strip() if len(row) > 2 else ''
            extra = ' | '.join(row[3:]) if len(row) > 3 else ''
            trending_topics.append({
                'rank': rank,
                'name': name,
                'volume': volume,
                'extra': extra
            })

print(f'\nExtracted {len(trending_topics)} trending topics:')
for t in trending_topics:
    print(f"{t['rank']}. {t['name']} | Volume: {t['volume']} | {t['extra'][:80]}")

# Also extract hashtag trends with duration
print('\n=== HASHTAG TRENDS WITH DURATION ===')
hashtag_trends = []
for i, (tag, cls, text) in enumerate(parser.all_texts):
    if text.startswith('#') and len(text) > 2:
        # Look for duration nearby
        duration = ''
        for j in range(i+1, min(i+5, len(parser.all_texts))):
            t = parser.all_texts[j][2]
            if 'hour' in t or 'min' in t:
                duration = t
                break
        hashtag_trends.append({'name': text, 'duration': duration})

for h in hashtag_trends:
    print(f"  {h['name']} - Trending for: {h['duration']}")

# Now parse trends24.in for the most recent hour's trends
print('\n=== TRENDS24.IN - MOST RECENT TRENDS ===')
with open('/tmp/trends24.html', 'r', encoding='utf-8', errors='ignore') as f:
    html2 = f.read()

parser2 = TableExtractor()
parser2.feed(html2)

# trends24 uses ordered lists (ol) with list items (li) containing trend names
# Let's extract from the first list-container (most recent hour)
class OLExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ol = False
        self.in_li = False
        self.in_a = False
        self.trends = []
        self.current_text = ''
        self.ol_count = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        if tag == 'ol' and 'trend' in cls:
            self.in_ol = True
            self.ol_count += 1
        elif tag == 'li' and self.in_ol:
            self.in_li = True
            self.current_text = ''
        elif tag == 'a' and self.in_li:
            self.in_a = True
            
    def handle_endtag(self, tag):
        if tag == 'ol':
            self.in_ol = False
        elif tag == 'li' and self.in_li:
            self.in_li = False
            text = self.current_text.strip()
            if text:
                self.trends.append({'text': text, 'hour_block': self.ol_count})
        elif tag == 'a':
            self.in_a = False
            
    def handle_data(self, data):
        if self.in_li:
            self.current_text += data

ol_parser = OLExtractor()
ol_parser.feed(html2)

print(f'Total trends from trends24: {len(ol_parser.trends)}')

# Show first hour block (most recent)
hour1_trends = [t for t in ol_parser.trends if t['hour_block'] == 1]
print(f'\nMost recent hour ({len(hour1_trends)} trends):')
for i, t in enumerate(hour1_trends):
    print(f"  {i+1}. {t['text']}")

hour2_trends = [t for t in ol_parser.trends if t['hour_block'] == 2]
print(f'\nPrevious hour ({len(hour2_trends)} trends):')
for i, t in enumerate(hour2_trends[:20]):
    print(f"  {i+1}. {t['text']}")
