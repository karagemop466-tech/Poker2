#!/usr/bin/env python3
"""Build a plain-text index from static site table rows for cross-page search."""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git'}

class TableRows(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_row=False; self.in_table=False; self.in_thead=False; self.current=[]; self.current_links=[]; self.rows=[]; self.title=''; self.in_title=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='title': self.in_title=True
        if tag=='table': self.in_table=True
        if tag=='thead': self.in_thead=True
        if tag=='tr' and self.in_table:
            self.in_row=True; self.current=[]; self.current_links=[]
        if tag=='a' and self.in_row and attrs.get('href'): self.current_links.append(attrs['href'])
        if self.in_row and tag in ('br','p','li'): self.current.append(' ')
    def handle_endtag(self, tag):
        if tag=='title': self.in_title=False
        if tag=='thead': self.in_thead=False
        if tag=='tr' and self.in_row:
            text=' '.join(''.join(self.current).split())
            if text and not self.in_thead:
                self.rows.append((text,list(dict.fromkeys(self.current_links))))
            self.in_row=False
        if tag=='table': self.in_table=False
    def handle_data(self,data):
        if self.in_title: self.title+=data
        if self.in_row: self.current.append(data)

files=[]
for path in ROOT.rglob('*.html'):
    if any(part in EXCLUDED for part in path.parts) or any(part.startswith('.') for part in path.relative_to(ROOT).parts): continue
    # Ignore workflow/build caches; index actual published HTML files only.
    files.append(path)
entries=[]
for path in sorted(files):
    parser=TableRows()
    try: parser.feed(path.read_text(encoding='utf-8'))
    except (OSError,UnicodeDecodeError): continue
    page=path.relative_to(ROOT).as_posix()
    for text,links in parser.rows:
        entries.append({'page':page,'title':parser.title.strip() or page,'text':text,'links':links})
output=ROOT/'data'/'site-search.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps({'generated_from':'published HTML table rows','row_count':len(entries),'rows':entries},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print(f'Indexed {len(entries)} table rows from {len(files)} HTML files.')
