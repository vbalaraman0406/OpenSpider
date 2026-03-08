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

# Print TABLE 1 (Race Classification) fully
print('=== TABLE 1: RACE CLASSIFICATION ===')
for row in parser.tables[1]:
    print(' | '.join(row))

# Print TABLE 0 (Qualifying) fully  
print('\n=== TABLE 0: QUALIFYING ===')
for row in parser.tables[0]:
    print(' | '.join(row))
