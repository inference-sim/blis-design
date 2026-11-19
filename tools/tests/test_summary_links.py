"""Every link from a summary or the index into the full design resolves."""
import pathlib
import re
import tempfile
import unittest

from support import copy_site, LATEST, LATEST_DIR

import build  # noqa: E402  (tools/ is on sys.path via support)

LINKING_PAGES = ("blis-design-3-pages.html", "blis-design-7-pages.html", "index.html")
FULL = "blis-target-design.html"
HREF = re.compile(r'href="([^"]*)"')


def link_problems(folder):
    """Return the broken links of the built pages in `folder`, as strings."""
    folder = pathlib.Path(folder)
    ids = set(re.findall(r'\bid="([^"]+)"', (folder / FULL).read_text()))
    problems = []
    for name in LINKING_PAGES:
        for href in HREF.findall((folder / name).read_text()):
            page, _, anchor = href.partition("#")
            if "v1.0.0" in href or href.startswith(("/", ".")):
                problems.append(f"{name}: {href} leaves this version")
            elif page == FULL and anchor and anchor not in ids:
                problems.append(f"{name}: {href} has no target in the full design")
            elif name != "index.html" and page in LINKING_PAGES:
                problems.append(f"{name}: {href} links a page other than the full design")
    return problems


class TestSummaryLinks(unittest.TestCase):
    def build_copy(self, tmp, edit=None):
        root = copy_site(tmp)
        if edit:
            path = root / f"{LATEST_DIR}/src/summary-3.html"
            path.write_text(edit(path.read_text()))
        build.build(LATEST, root=root)
        return root / LATEST_DIR

    def test_summary_links_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(link_problems(self.build_copy(tmp)), [])

    def test_a_broken_anchor_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.build_copy(tmp, lambda t: t + '<p><a href="blis-target-design.html#s99-9">x</a></p>')
            self.assertEqual(len(link_problems(folder)), 1)

    def test_a_link_into_v1_or_the_root_is_found(self):
        for bad in ("../v1.0.0/blis-target-design.html#s2", "/blis-target-design.html#s2",
                    "../blis-target-design.html#s2", "blis-design-7-pages.html#s2"):
            with tempfile.TemporaryDirectory() as tmp:
                folder = self.build_copy(tmp, lambda t: t + f'<p><a href="{bad}">x</a></p>')
                self.assertEqual(len(link_problems(folder)), 1, bad)


if __name__ == "__main__":
    unittest.main()
