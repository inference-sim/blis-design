"""check.py and standcheck.py on fixture pages and on the built design of the latest version."""
import pathlib
import tempfile
import unittest

from support import REPO, run_tool, LATEST, LATEST_DIR

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>t</title>
<meta name="description" content="{desc}">
</head><body><main>
<h2 id="s1"><span class="secno">1</span>One</h2>
{body}
</main></body></html>
"""
CLEAN = "<p>The design states what must hold. A trigger test is <span class=\"inv\">T-E1</span>.</p>"


def standcheck(body="", desc="The standing design of BLIS."):
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "page.html"
        page.write_text(PAGE.format(desc=desc, body=body))
        return run_tool(REPO, "tools/standcheck.py", page)


class TestStandcheck(unittest.TestCase):
    def test_clean_section_passes_and_trigger_ids_are_allowed(self):
        done = standcheck(CLEAN + "<p>Trigger T-E1 and T-M1 name outcomes.</p>")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_standcheck_rejects_release_content(self):
        for text in ("<p>It changed on 2026-11-19.</p>",
                     "<p>This is scheduled for M3.2.</p>",
                     "<p>A rule stays until a MINOR version adds the check.</p>",
                     "<p>It holds until a MAJOR version adds it.</p>",
                     "<p>The figure is current today.</p>"):
            done = standcheck(text)
            self.assertNotEqual(done.returncode, 0, text)
            self.assertIn("violations", done.stdout)

    def test_standcheck_scans_the_meta_description(self):
        for desc in ("Design for the next release of BLIS.", "Written 2026-11-19.", "Plan for M3.2."):
            done = standcheck(CLEAN, desc=desc)
            self.assertNotEqual(done.returncode, 0, desc)
        self.assertEqual(standcheck(CLEAN, desc="The standing design of BLIS.").returncode, 0)

    def test_built_v2_pages_pass_check(self):
        for name in ("blis-target-design.html", "blis-design-3-pages.html", "blis-design-7-pages.html", "index.html"):
            done = run_tool(REPO, "tools/check.py", REPO / LATEST_DIR / name)
            self.assertEqual(done.returncode, 0, name + "\n" + done.stdout)
            self.assertIn("KB", done.stdout)

    def test_built_v2_summaries_pass_standcheck(self):
        for name in ("blis-design-3-pages.html", "blis-design-7-pages.html", "index.html"):
            done = run_tool(REPO, "tools/standcheck.py", REPO / LATEST_DIR / name)
            self.assertEqual(done.returncode, 0, name + "\n" + done.stdout)

    def test_built_v2_full_design_passes_standcheck(self):
        done = run_tool(REPO, "tools/standcheck.py", REPO / f"{LATEST_DIR}/blis-target-design.html")
        self.assertEqual(done.returncode, 0, done.stdout)


class TestCheck(unittest.TestCase):
    def run_check(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            page = pathlib.Path(tmp) / "page.html"
            page.write_text(PAGE.format(desc="d", body=body))
            return run_tool(REPO, "tools/check.py", page)

    def test_check_passes_on_a_sound_page(self):
        self.assertEqual(self.run_check('<p>See <a href="#s1">§1</a>.</p>').returncode, 0)

    def test_check_flags_broken_anchor_and_unresolved_reference(self):
        done = self.run_check('<p><a href="#nowhere">x</a> and §9.9</p>')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("nowhere", done.stdout)
        self.assertIn("9.9", done.stdout)

    def test_check_flags_a_rule_cited_but_never_defined(self):
        done = self.run_check('<p><span class="inv">X99</span></p>')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("X99", done.stdout)


if __name__ == "__main__":
    unittest.main()
