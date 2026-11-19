"""The design is a standing document: no dates, milestones, status or references
to the current release anywhere in it, including its meta description.

    python3 -I tools/standcheck.py v2.0.0/blis-target-design.html

Scans the text of <main> (or of <body> on a page without one) and the meta description. Prints each violation with
context, then a count, and exits 1 when the count is not zero.
"""
import html
import re
import sys

PATTERN = re.compile(
    r"\btoday\b"
    r"|\bM[0-9]+(?:\.[0-9]+)*\b"                        # milestone labels: M1, M3.2
    r"|\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b"                # bare ISO dates
    r"|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) 20[0-9]{2}\b"
    r"|#[0-9]{2,4}\b"                                   # issue and pull-request numbers
    r"|\bcurrently\b|\bfor now\b|\bnot yet\b|\bnext release\b|\bthis release\b|\bupcoming\b"
    r"|\buntil an? (?:MAJOR|MINOR|PATCH) version adds\b",
    re.I,
)
# A trigger test identifier such as T-M1 or T-E1 sits right after the two context characters;
# "not yet priced" and its kin are ordinary phrases about a cost.
ALLOWED = (
    lambda context: context.startswith("T-"),
    lambda context: re.search(r"not yet (?:priced|classified|explain|known)", context, re.I),
)


def violations(page):
    description = re.search(r'<meta name="description" content="([^"]*)"', page)
    start = page.find("<main>")
    if start < 0:
        start = page.find("<body>")
    body = re.sub(r"<(style|script)\b.*?</\1>", " ", page[max(start, 0):], flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    if description:
        text = html.unescape(description.group(1)) + "\n" + text
    found = []
    for m in PATTERN.finditer(text):
        context = text[max(0, m.start() - 2):m.end() + 12]
        if any(allowed(context) for allowed in ALLOWED):
            continue
        found.append(text[max(0, m.start() - 70):m.end() + 40].replace("\n", " "))
    return found


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    found = violations(open(argv[1]).read())
    for line in found:
        print("|", line)
    print("violations", len(found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
