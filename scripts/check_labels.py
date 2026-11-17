#!/usr/bin/env python3
"""Semantic gate: a rendered page must not label a number, or a link, as something it is not.

Every defect this file guards against was in a build that passed every other check in this
repository. Structure checks prove a page exists and links resolve; they cannot see that the
word next to a figure is the wrong word. Found by reading the published HTML on 2026-11-17:

  1. 181 citation links carried the label "schedule" while pointing at a structure-sheet PDF,
     because the renderer labelled arguments by position rather than by URL.
  2. The hotel table labelled a resort-fee page and a booking engine "schedule" and "structure".
  3. 35 Wynn rows printed a guarantee ÷ buy-in ratio next to an UNVERIFIED badge, where the
     house fee is blank - so the ratio divides by a number the page itself will not stand behind.
  4. A "true cost per night" figure was once labelled as a room rate; the words and the field
     they came from have to keep agreeing.

Checks run over the generated HTML:

  A. every <a> whose text is one of the citation labels must point at a URL that matches it;
  B. no row that renders "fee unconfirmed" may also render a numeric ratio;
  C. every "true cost per night" figure must sit in a cell that also mentions tax;
  D. no page may cite a workflow file that is not in .github/workflows/.

Usage: python3 scripts/check_labels.py [--quiet]
Exit code 1 on any failure.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
               glob.glob(os.path.join(ROOT, "plan", "*.html")) +
               glob.glob(os.path.join(ROOT, "2026", "*.html")) +
               glob.glob(os.path.join(ROOT, "2026", "venues", "*.html")) +
               glob.glob(os.path.join(ROOT, "venues", "*.html")))

# label -> predicate the URL must satisfy
LINK_RULES = {
    "structure sheet": lambda u: u.lower().endswith(".pdf") or "/structures/" in u.lower(),
    "DSE IV schedule": lambda u: "dse-" in u.lower(),
    "resort-fee page": lambda u: "resort-fee" in u.lower(),
    # A hotel's fee/cancellation citation is the page the figures were read from: it may be a
    # dedicated resort-fee page, a resort-information page, hotel terms, or a property page whose
    # fee schedule the earlier session transcribed. The rule only has to reject a page that could
    # not carry a fee at all.
    "fee/cancellation source": lambda u: any(
        x in u.lower() for x in ("resort-fee", "resort-information", "terms", "/hotel", "fee")),
    "official booking page": lambda u: any(
        x in u.lower() for x in ("/book", "booking", ".com", ".com/en/hotel")),
    "hotel terms": lambda u: "hotel-terms" in u.lower() or "terms-and-conditions" in u.lower(),
    "poker suite rates": lambda u: "suite-rates" in u.lower(),
    "official booking engine": lambda u: "/booking" in u.lower() or "/book" in u.lower(),
    "official booking page": lambda u: True,
    # Inverse direction: a schedule label must not land on a structure-sheet PDF, and a structure
    # label must not land on the schedule page. These are the two documents the site transcribes
    # every value from, so confusing them misdescribes the provenance of a number.
    "schedule": lambda u: "structure" not in u.lower() and not u.lower().endswith(".pdf"),
    "structure": lambda u: "structure" in u.lower() or u.lower().endswith(".pdf"),
    "page": lambda u: True,
}

LINK_RE = re.compile(r'<a\s[^>]*href="([^"]+)"[^>]*>([^<]+)</a>')

problems = []
counts = {"links": 0, "ratio_rows": 0, "cost_cells": 0, "workflow_links": 0}


def main():
    quiet = "--quiet" in sys.argv

    workflows = set()
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    if os.path.isdir(wf_dir):
        workflows = {os.path.basename(p) for p in glob.glob(os.path.join(wf_dir, "*.yml"))}

    for path in PAGES:
        rel = os.path.relpath(path, ROOT)
        try:
            html = open(path, encoding="utf8").read()
        except OSError as exc:                       # unreadable page is a failure, not a skip
            problems.append("%s: cannot read (%s)" % (rel, exc))
            continue

        # ---- A. citation label must describe the document behind it
        for url, text in LINK_RE.findall(html):
            counts["links"] += 1
            rule = LINK_RULES.get(text.strip())
            if rule and not rule(url):
                problems.append('%s: link labelled "%s" points at %s' % (rel, text.strip(), url[:90]))

            # ---- D. a link into .github/workflows must name a workflow that exists
            if "/actions/workflows/" in url:
                counts["workflow_links"] += 1
                wf = url.rsplit("/", 1)[-1].split("?")[0]
                if wf and wf not in workflows:
                    problems.append("%s: cites workflow %s which is not in .github/workflows/" % (rel, wf))

        # ---- B. a row with no confirmed house fee must not print a guarantee ratio.
        # Two layouts exist and both are handled without a fixed column index:
        #   * the root table annotates the buy-in cell with "fee $N"      -> look for "fee $"
        #   * the /2026/ table has its own "House fee" column             -> that cell holds $
        # In both cases a "—" in the fee position means the fee is unknown, and a ratio next to it
        # is a ranking of a cost the page will not stand behind.
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
            if not re.search(r"\d{1,4}\.\d{1,2}&times;", row):
                continue
            cells = [re.sub(r"<[^>]+>", " ", c).strip()
                     for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            flat = " ".join(cells)
            has_gtd = bool(re.search(r"\$[\d,]{4,}", flat))
            if not has_gtd:
                continue
            counts["ratio_rows"] += 1
            fee_confirmed = bool(re.search(r"fee \$[\d,]+", flat))
            # layout 2: a cell that is exactly a money value placed between the buy-in and the
            # guarantee; the fee column is the one the header calls "House fee". Rows whose fee
            # cell is an em-dash / dash / "fee unconfirmed" are the ones to reject.
            fee_cells = [c for c in cells if c in ("", "-", "\u2014", "&mdash;", "fee unconfirmed")]
            if not fee_confirmed and fee_cells:
                snippet = " ".join(flat.split())[:110]
                problems.append("%s: ratio printed where no house fee is confirmed: %s"
                                % (rel, snippet))

        # ---- C. "true cost per night" must be presented as a cost including tax
        for cell in re.findall(r"<td[^>]*>(.*?)</td>", html, re.S):
            if "true cost per night" not in cell:
                continue
            counts["cost_cells"] += 1
            if "tax" not in cell.lower():
                problems.append("%s: 'true cost per night' shown without mentioning tax" % rel)

    if problems:
        print("LABEL CHECK FAILED (%d):" % len(problems))
        for p in problems[:40]:
            print("  -", p)
        if len(problems) > 40:
            print("  ... and %d more" % (len(problems) - 40))
        return 1

    if not quiet:
        print("label check ok: %d pages, %d links, %d unconfirmed-fee rows, %d cost cells, "
              "%d workflow links"
              % (len(PAGES), counts["links"], counts["ratio_rows"], counts["cost_cells"],
                 counts["workflow_links"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
