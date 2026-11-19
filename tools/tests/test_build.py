"""The v2.0.0 build: seed fidelity, staleness, ordering and ignored sources."""
import re
import tempfile
import unittest
import pathlib

from support import PAGES, REPO, copy_site, git_show, run_tool, strip_topbar

import build  # noqa: E402  (tools/ is on sys.path via support)

DESCRIPTION = re.compile(r'<meta name="description" content="[^"]*">')


def normalise(html):
    return DESCRIPTION.sub('<meta name="description" content="">', strip_topbar(html))


class TestBuild(unittest.TestCase):
    def test_seed_round_trips_v1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            written = build.build("2.0.0", root=root)
            self.assertEqual(sorted(p.name for p in written), sorted(PAGES))
            for name in PAGES:
                built = (root / "v2.0.0" / name).read_text()
                self.assertIn('<meta name="blis-design-version" content="2.0.0">', built, name)
                v1 = git_show("v1.0.0", name).decode()
                self.assertEqual(normalise(built), normalise(v1),
                                 f"{name}: the seed must reproduce v1.0.0 apart from the top bar and description")

    def test_committed_pages_match_the_sources(self):
        self.assertEqual(build.stale("2.0.0"), [])

    def test_description_has_no_release_wording(self):
        head = (REPO / "v2.0.0/src/head.html").read_text()
        desc = DESCRIPTION.search(head).group(0).lower()
        for word in ("next release", "this release", "upcoming", "today", "target design for"):
            self.assertNotIn(word, desc)

    def test_check_flags_stale_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            clean = run_tool(root, "tools/build.py", "2.0.0", "--check")
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            section = root / "v2.0.0/src/08-s8.html"
            section.write_text(section.read_text() + "<p>An edit with no rebuild.</p>\n")
            stale = run_tool(root, "tools/build.py", "2.0.0", "--check")
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("v2.0.0/blis-target-design.html", stale.stdout + stale.stderr)
            self.assertNotIn("blis-design-3-pages", stale.stdout + stale.stderr)
            # The check compares; it must not write.
            self.assertNotIn("An edit with no rebuild", (root / "v2.0.0/blis-target-design.html").read_text())
            fixed = run_tool(root, "tools/build.py", "2.0.0")
            self.assertEqual(fixed.returncode, 0, fixed.stderr)
            self.assertEqual(run_tool(root, "tools/build.py", "2.0.0", "--check").returncode, 0)

    def test_check_flags_a_summary_edit_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            src = root / "v2.0.0/src/summary-3.html"
            src.write_text(src.read_text().replace("What BLIS is", "What BLIS is, again"))
            out = run_tool(root, "tools/build.py", "2.0.0", "--check")
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("v2.0.0/blis-design-3-pages.html", out.stdout + out.stderr)

    def test_toc_matches_source_order(self):
        # Real sources: the table of contents lists v1.0.0's sections in v1.0.0's order.
        v1 = git_show("v1.0.0", "blis-target-design.html").decode()
        built = (REPO / "v2.0.0/blis-target-design.html").read_text()
        toc = lambda h: re.findall(r'<li><a href="#([^"]+)">([^<]*)</a></li>', h[h.index('<nav class="toc"'):h.index("</nav>")])
        self.assertEqual(toc(built), toc(v1))
        # Fixture sources: order follows file names, not identifiers or titles.
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            src = root / "v2.0.0/src"
            for f in src.glob("[0-9][0-9]-*.html"):
                if f.name != "00-front.html":
                    f.unlink()
            (src / "01-zeta.html").write_text('<h2 id="zeta"><span class="secno">1</span>Zeta: first</h2>\n<p>z</p>\n')
            (src / "02-alpha.html").write_text('<h2 id="alpha"><span class="secno">2</span>Alpha</h2>\n<p>a</p>\n')
            build.build("2.0.0", root=root)
            html = (root / "v2.0.0/blis-target-design.html").read_text()
            self.assertEqual(toc(html), [("zeta", "1 Zeta"), ("alpha", "2 Alpha")])
            self.assertLess(html.index('id="zeta"'), html.index('id="alpha"'))

    def test_build_ignores_underscore_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            src = root / "v2.0.0/src"
            (src / "_scratch.html").write_text('<h2 id="scratch"><span class="secno">9</span>Scratch</h2><p>SCRATCH-MARK</p>\n')
            (src / "_idmap").mkdir()
            (src / "_idmap/ids.tsv").write_text("X1\tkept\n")
            (src / "_idmap/17-notes.html").write_text("<p>SCRATCH-MARK</p>")
            (src / "_00-front.html").write_text("<p>SCRATCH-MARK</p>")
            before = {p.name: p.read_text() for p in (root / "v2.0.0").glob("*.html")}
            build.build("2.0.0", root=root)
            for p in (root / "v2.0.0").glob("*.html"):
                self.assertNotIn("SCRATCH-MARK", p.read_text(), p.name)
                self.assertEqual(p.read_text(), before[p.name], p.name)
            self.assertEqual(run_tool(root, "tools/build.py", "2.0.0", "--check").returncode, 0)

    def test_build_refuses_a_section_without_a_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            (root / "v2.0.0/src/17-bad.html").write_text("<p>no heading</p>\n")
            out = run_tool(root, "tools/build.py", "2.0.0")
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("17-bad.html", out.stdout + out.stderr)

    def test_landing_page_is_built_from_versions_json(self):
        self.assertEqual(build.landing_stale(), False)
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_site(tmp)
            (root / "index.html").write_text("old")
            out = run_tool(root, "tools/build.py", "--landing", "--check")
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("index.html", out.stdout + out.stderr)
            self.assertEqual(run_tool(root, "tools/build.py", "--landing").returncode, 0)
            self.assertEqual(run_tool(root, "tools/build.py", "--landing", "--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
