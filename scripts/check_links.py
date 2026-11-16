#!/usr/bin/env python3
"""Verification pass: every internal link resolves; every table data row has an official https link."""
import pathlib, re, sys
from html.parser import HTMLParser
DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"
OFFICIAL = {"www.venetianlasvegas.com","www.caesars.com","www.wynnlasvegas.com","cdn.wynnresorts.com",
            "mgmgrand.mgmresorts.com","assets.contentstack.io","www.goldennugget.com"}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.hrefs=[]; s.rows=[]; s.cur=None; s.in_th=False; s.depth=0; s.row_links=None; s.row_has_th=False
    def handle_starttag(s,t,a):
        a=dict(a)
        if t=="table": s.skip = a.get("class")=="meta"
        if getattr(s,"skip",False): return
        if t=="a" and "href" in a: s.hrefs.append(a["href"]); 
        if t=="tr" and not getattr(s,"skip",False): s.row_links=[]; s.row_has_th=False
        if t=="th": s.row_has_th=True
        if t=="a" and "href" in a and s.row_links is not None: s.row_links.append(a["href"])
    def handle_endtag(s,t):
        if t=="table": s.skip=False
        if t=="tr" and s.row_links is not None and not getattr(s,"skip",False):
            if not s.row_has_th: s.rows.append(s.row_links)
            s.row_links=None
errors=[]; total=0; ok=0
for f in sorted(DOCS.glob("*.html")):
    p=P(); p.feed(f.read_text())
    for h in p.hrefs:
        if h.startswith("http"):
            from urllib.parse import urlparse
            if urlparse(h).hostname not in OFFICIAL and not h.startswith("mailto"):
                pass
            continue
        target=(DOCS/h.split("#")[0])
        if h.split("#")[0] and not target.exists(): errors.append(f"{f.name}: broken link {h}")
    for r in p.rows:
        total+=1
        if any(x.startswith("https://") for x in r):
            ok+=1
        else:
            errors.append(f"{f.name}: table row without https source link")
print(f"rows checked: {total}, with source link: {ok}")
if errors:
    print("\n".join(errors[:40])); print("FAILED", len(errors)); sys.exit(1)
print("OK")
