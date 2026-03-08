from html.parser import HTMLParser

with open('/Users/vbalaraman/OpenSpider/ausgp.html', 'r', encoding='utf-8') as f:
    html = f.read()

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = ''
        self.depth = 0
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'table':
            cls = attrs_dict.get('class', '')
            if 'wikitable' in cls:
                self.in_table = True
                self.current_table = []
                self.depth += 1
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ['td', 'th'] and self.in_row:
            self.in_cell = True
            self.current_cell = ''
        elif tag == 'br' and self.in_cell:
            self.current_cell += ' '
    def handle_endtag(self, tag):
        if tag == 'table' and self.in_table:
            self.depth -= 1
            if self.depth <= 0:
                self.in_table = False
                self.tables.append(self.current_table)
                self.current_table = []
                self.depth = 0
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if self.current_row:
                self.current_table.append(self.current_row)
        elif tag in ['td', 'th'] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

parser = TableParser()
parser.feed(html)

print(f'Total tables: {len(parser.tables)}')

# Print ONLY rows 11-20 of race classification (Table 1)
print('\n=== RACE CLASSIFICATION (rows 11+) ===')
for row in parser.tables[1][11:]:
    print(' | '.join(row))

# Check all tables for practice data
for i in range(len(parser.tables)):
    if i not in [0, 1]:
        print(f'\n=== TABLE {i} ({len(parser.tables[i])} rows) ===')
        for row in parser.tables[i][:3]:
            print(' | '.join(row))

# Search for practice, weather, incidents in text
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            self.result.append(data)

tx = TextExtractor()
tx.feed(html)
text = ' '.join(tx.result)

for term in ['Race report', 'weather', 'Piastri', 'incident', 'fastest lap', 'tyre', 'tire']:
    idx = text.lower().find(term.lower())
    if idx != -1:
        print(f'\n=== Found "{term}" ===')
        print(text[max(0,idx-50):idx+300])
