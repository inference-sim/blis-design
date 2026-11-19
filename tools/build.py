"""Build the design pages of one version from its sources.

    python3 -I tools/build.py 2.0.0            write v2.0.0/*.html
    python3 -I tools/build.py 2.0.0 --check    compare instead of write; exit 1 and name stale pages
    python3 -I tools/build.py --landing        write the root index.html from versions.json
    python3 -I tools/build.py --landing --check

Sources live in v<version>/src/. Anything whose name starts with an underscore
is a working note and is ignored. The files are:

    head.html            <meta> and <title> elements of the full design's head
    style.css            the full design's style sheet
    00-front.html        the title header and abstract (no <h2>)
    NN-<id>.html         one section each, in file-name order; the table of contents is
                         generated from their <h2 id="..."> headings
    footer.html          the closing <footer>
    summary-3.html, summary-7.html, index.html
                         the body of the other three pages, each with a
                         <name>.head.html holding its <title> and style

The build adds the top bar (tools/site/topbar.html) and the version meta to every page.
Standard library only.
"""
import argparse
import html as htmllib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sitelib  # noqa: E402

ROOT = sitelib.ROOT
FULL = "blis-target-design.html"
OTHER_PAGES = {
    "blis-design-3-pages.html": "summary-3",
    "blis-design-7-pages.html": "summary-7",
    "index.html": "index",
}
SECTION_FILE = re.compile(r"^\d\d-[^_].*\.html$")
HEADING = re.compile(r'<h2 id="([^"]+)">(?:<span class="secno">([^<]*)</span>)?(.*?)</h2>', re.S)


def _read(src, name):
    return (src / name).read_text()


def _section_files(src):
    return sorted(p for p in src.iterdir()
                  if p.is_file() and not p.name.startswith("_") and SECTION_FILE.match(p.name)
                  and p.name != "00-front.html")


def _toc(section_texts):
    items = []
    for name, text in section_texts:
        found = HEADING.findall(text)
        if not found:
            raise ValueError(f"{name}: a section file needs an <h2 id=\"...\"> heading")
        for ident, secno, title in found:
            title = htmllib.unescape(re.sub(r"<[^>]+>", "", title)).split(":")[0].strip()
            label = f"{secno} {title}" if secno else title
            items.append(f'    <li><a href="#{ident}">{htmllib.escape(label, quote=False)}</a></li>')
    return "\n".join(items)


def render(version, root=ROOT):
    """Return {page name: text} for every page of one version."""
    root = pathlib.Path(root)
    src = root / f"v{version}" / "src"
    if not src.is_dir():
        raise FileNotFoundError(f"no sources at {src}")
    pages = {}

    sections = [(p.name, p.read_text()) for p in _section_files(src)]
    main = (
        _read(src, "00-front.html")
        + "".join(text for _, text in sections)
        + _read(src, "footer.html")
    )
    full = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        + _read(src, "head.html")
        + "<style>\n" + _read(src, "style.css") + "</style>\n\n</head>\n<body>\n"
        + '<div class="layout">\n<nav class="toc" aria-label="Contents">\n'
        + '  <div class="toc-title">Contents</div>\n  <ol>\n'
        + _toc(sections) + "\n  </ol>\n</nav>\n<main>\n" + main + "</main>\n</div>\n</body>\n</html>\n"
    )
    pages[FULL] = full

    for name, stem in OTHER_PAGES.items():
        pages[name] = (
            '<!doctype html>\n<html lang="en">\n<head>\n'
            + _read(src, f"{stem}.head.html")
            + "</head>\n<body>\n" + _read(src, f"{stem}.html") + "</body>\n</html>\n"
        )

    return {name: sitelib.insert_topbar(text, version, root) for name, text in pages.items()}


def build(version, root=ROOT):
    """Write v<version>/*.html and return the paths written."""
    root = pathlib.Path(root)
    written = []
    for name, text in render(version, root).items():
        path = root / f"v{version}" / name
        path.write_text(text)
        written.append(path)
    return written


def stale(version, root=ROOT):
    """Paths of built pages that differ from what the sources produce."""
    root = pathlib.Path(root)
    out = []
    for name, text in render(version, root).items():
        path = root / f"v{version}" / name
        if not path.is_file() or path.read_text() != text:
            out.append(path)
    return out


def landing_stale(root=ROOT):
    root = pathlib.Path(root)
    expected = sitelib.render_landing(sitelib.load_versions(root), root)
    path = root / "index.html"
    return not path.is_file() or path.read_text() != expected


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", nargs="?", help="design version, such as 2.0.0")
    ap.add_argument("--check", action="store_true", help="compare instead of write")
    ap.add_argument("--landing", action="store_true", help="the root index.html")
    args = ap.parse_args(argv)
    if args.landing == bool(args.version):
        ap.error("give either a version or --landing")

    if args.landing:
        if args.check:
            if landing_stale():
                print("stale: index.html (rebuild with: python3 -I tools/build.py --landing)")
                return 1
            print("index.html is up to date")
            return 0
        (ROOT / "index.html").write_text(sitelib.render_landing(sitelib.load_versions()))
        print("wrote index.html")
        return 0

    try:
        if args.check:
            bad = stale(args.version)
            for path in bad:
                print(f"stale: {path.relative_to(ROOT)} (rebuild with: python3 -I tools/build.py {args.version})")
            if not bad:
                print(f"v{args.version} is up to date")
            return 1 if bad else 0
        for path in build(args.version):
            print(f"wrote {path.relative_to(ROOT)}")
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
