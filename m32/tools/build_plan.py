#!/usr/bin/env python3
"""Generate m32/plan.html from its sources, so the plan never drifts from the requirements.

plan.html = plan.preamble.md  (delivered M1-M3.1 summary + abstract, plan-authored)
          + requirements.md    (THE SOURCE OF TRUTH for every M3.2 number and rule)
          + plan.appendix.md   (plan-authored execution table)

all rendered to the release-plan gist's HTML style (tools/plan.css).

Usage:
  python3 m32/tools/build_plan.py            # write m32/plan.html
  python3 m32/tools/build_plan.py --check    # exit 1 if the committed plan.html is stale

Only the markdown subset the three sources use is supported: ATX headings (#..####),
paragraphs, `-`/`*` bullet lists (one level of nesting, wrapped continuations), GFM tables,
blockquotes, and the inline `**bold**` / `*italic*` / `` `code` `` / `[text](url)`.
No third-party dependency (X21): pure standard library.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
M32 = HERE.parent

_slugs: dict = {}


def slug(text: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-") or "s"
    n = _slugs.get(base, 0)
    _slugs[base] = n + 1
    return base if n == 0 else f"{base}-{n}"


DESIGN_URL = "https://inference-sim.github.io/blis-design/v2.3.0/blis-target-design.html"
_DESIGN_REF = re.compile(r"design (§\d+(?:\.\d+)?(?:(?:, | and |, and )§\d+(?:\.\d+)?)*)")


def link_design_sections(text: str) -> str:
    """Turn `design §n.m` (and the `, §x.y` / ` and §x.y` that follow it) into links to the design.

    A bare § number is this file's own section, so only text that says "design" is linked.
    Text inside an existing link is left alone."""
    def one(m):
        return re.sub(
            r"§(\d+)(?:\.(\d+))?",
            lambda s: (f'<a href="{DESIGN_URL}#s{s.group(1)}-{s.group(2)}">{s.group(0)}</a>' if s.group(2)
                       else f'<a href="{DESIGN_URL}#s{s.group(1)}">{s.group(0)}</a>'),
            m.group(0))
    parts = re.split(r"(<a .*?</a>)", text)
    return "".join(p if p.startswith("<a ") else _DESIGN_REF.sub(one, p) for p in parts)


def inline(text: str) -> str:
    """Render inline markdown. Code spans are stashed as placeholders so bold/italic/links may
    span them (e.g. **a `code` b**), then restored after the other rules run."""
    codes: list = []

    def stash(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = link_design_sections(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)
    return text


def render(md: str, headings: list) -> str:
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl == 2:
                sid = slug(txt)
                headings.append((sid, txt))
                out.append(f'<h2 id="{sid}">{inline(txt)}</h2>')
            else:
                out.append(f"<h{lvl}>{inline(txt)}</h{lvl}>")
            i += 1
        elif line.lstrip().startswith("> "):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
        elif line.lstrip().startswith("|"):
            buf = []
            while i < n and lines[i].lstrip().startswith("|"):
                buf.append(lines[i].strip())
                i += 1
            out.append(table(buf))
        elif re.match(r"^(\s*)[-*]\s+", line):
            block = []
            while i < n and (re.match(r"^(\s*)[-*]\s+", lines[i]) or
                             (lines[i].startswith("  ") and lines[i].strip())):
                block.append(lines[i])
                i += 1
            out.append(ul(block))
        else:  # paragraph: join wrapped lines
            buf = []
            while i < n and lines[i].strip() and not re.match(
                    r"^(#{1,4}\s|\s*[-*]\s|\s*\||\s*>)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


def ul(block: list) -> str:
    """One level of nesting, by leading-space width; wrapped continuations join their item."""
    items, cur, cur_indent = [], None, 0
    for ln in block:
        m = re.match(r"^(\s*)[-*]\s+(.*)$", ln)
        if m:
            if cur is not None:
                items.append(cur)
            cur = {"indent": len(m.group(1)), "text": m.group(2).strip(), "children": []}
            cur_indent = len(m.group(1))
        else:  # continuation of the current item's text
            if cur is not None:
                cur["text"] += " " + ln.strip()
    if cur is not None:
        items.append(cur)
    # fold deeper-indented items under the previous shallower one
    top, stack = [], []
    for it in items:
        if top and it["indent"] > top[-1]["indent"]:
            top[-1]["children"].append(it)
        else:
            top.append(it)
    def emit(nodes):
        s = ["<ul>"]
        for nd in nodes:
            inner = inline(nd["text"])
            if nd["children"]:
                inner += emit(nd["children"])
            s.append(f"<li>{inner}</li>")
        s.append("</ul>")
        return "".join(s)
    return emit(top)


def table(rows: list) -> str:
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    head = cells(rows[0])
    body = rows[2:] if len(rows) > 1 and all(re.match(r"^:?-+:?$", c) for c in cells(rows[1])) else rows[1:]
    out = ['<div class="tbl"><table>', "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def strip_h1_and_intro(md: str) -> str:
    """Drop requirements.md's own H1 title (the page H1 comes from the preamble)."""
    lines = md.split("\n")
    out, dropped = [], False
    for ln in lines:
        if not dropped and ln.startswith("# "):
            dropped = True
            continue
        out.append(ln)
    return "\n".join(out)


def build() -> str:
    _slugs.clear()
    css = (HERE / "plan.css").read_text(encoding="utf-8")
    preamble = (M32 / "plan.preamble.md").read_text(encoding="utf-8")
    requirements = strip_h1_and_intro((M32 / "requirements.md").read_text(encoding="utf-8"))
    appendix = (M32 / "plan.appendix.md").read_text(encoding="utf-8")

    headings: list = []
    # Preamble carries the page <h1>; take the first ATX H1 as title.
    m = re.search(r"^#\s+(.*)$", preamble, re.M)
    title = m.group(1).strip() if m else "BLIS M3.2 Plan"
    pre_body = re.sub(r"^#\s+.*$", "", preamble, count=1, flags=re.M)

    body = "\n".join([
        render(pre_body, headings),
        render(requirements, headings),
        render(appendix, headings),
    ])
    toc = "\n".join(f'    <li><a href="#{sid}">{html.escape(txt)}</a></li>' for sid, txt in headings)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="Generated M3.2 plan: delivered M1-M3.1 summary, the requirements body (source of truth), and execution order.">
{css}
</head>
<body>
<div class="layout">
<nav class="toc" aria-label="Contents">
  <div class="toc-title">Contents</div>
  <ol>
{toc}
  </ol>
</nav>
<main>
<header>
<h1>{inline(title)}</h1>
</header>
{body}
</main>
</div>
</body>
</html>
"""


def main(argv):
    out = M32 / "plan.html"
    generated = build()
    if "--check" in argv:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != generated:
            sys.stderr.write(
                "plan.html is stale: run `python3 m32/tools/build_plan.py` and commit.\n")
            return 1
        print("plan.html is up to date.")
        return 0
    out.write_text(generated, encoding="utf-8")
    print(f"wrote {out} ({len(generated)} bytes, {len(_slugs)} sections)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
