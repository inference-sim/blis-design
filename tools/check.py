"""Structural checks on a built design page.

    python3 -I tools/check.py v2.0.0/blis-target-design.html

Prints each finding group and exits 1 when any group is non-empty. Checks: every
#anchor link has a target; tags nest; every section reference resolves; every
cited rule identifier is defined; links whose text is a section number point at that
section. On a page without numbered sections (a summary), only anchors and nesting are checked. Prints the page size in kilobytes.
"""
import re
import sys
from html.parser import HTMLParser

VOID = {"meta", "br", "hr", "img", "input", "link", "path", "rect", "line", "circle", "polyline", "polygon"}
OPTIONAL_END = ("li", "p", "td", "tr", "th", "dd", "dt", "option")


class Nesting(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1] != tag and self.stack[-1] in OPTIONAL_END:
            self.stack.pop()
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append((tag, self.getpos()))


def check(text):
    """Return ({finding group: items}, kilobytes)."""
    ids = set(re.findall(r'id="([^"]+)"', text))
    hrefs = set(re.findall(r'href="#([^"]+)"', text))
    parser = Nesting()
    parser.feed(text)
    headings = {m.group(1) for m in re.finditer(r"<h[34][^>]*>(\d+\.\d+(?:\.\d+)?) ", text)}
    headings |= {m.group(1) for m in re.finditer(r'<h2 id="s(\d+)"', text)}
    refs_to_sections = {r for r in re.findall(r"§(\d+(?:\.\d+)*)", text) if r not in headings}
    defined = set(re.findall(
        r'<span class="inv">([A-Z]+(?:-[A-Z]+)?-?\d+)</span>\s*(?:<b>|<span class="stmt">| [A-Z])', text))
    cited = set(re.findall(r'<span class="inv">([A-Z]+(?:-[A-Z]+)?-?\d+)</span>', text))
    numbered = {m.group(2): m.group(1) for m in re.finditer(
        r'<h[23] id="([^"]+)">(?:<span class="secno">)?([0-9A-C]+(?:\.\d+)?)', text)}
    wrong_links = [(h, t) for h, t in re.findall(r'<a href="#([^"]+)">(§?\d+(?:\.\d+)?)</a>', text)
                   if t.lstrip("§") in numbered and numbered[t.lstrip("§")] != h]
    if not re.search(r'<h2 id="s\d', text):
        # A summary page cites sections of the full design, which it does not contain.
        refs_to_sections, cited, wrong_links = set(), set(), []
    findings = {
        "missing anchors": sorted(hrefs - ids),
        "nesting": parser.errors[:6] + [("open", t) for t in parser.stack[:6]],
        "unresolved § refs": sorted(refs_to_sections),
        "referenced, not defined": sorted(cited - defined),
        "section links pointing elsewhere": wrong_links,
    }
    return findings, len(text.encode()) // 1024


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    text = open(argv[1]).read()
    findings, kb = check(text)
    for name, items in findings.items():
        print(f"{name}: {items}")
    print("KB", kb)
    return 1 if any(findings.values()) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
