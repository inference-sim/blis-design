"""Behaviour of the versioned site: pages, version list, picker and redirects."""
import json
import re
import unittest
from urllib.parse import urljoin

from support import (PAGES, REPO, TOPBAR_RE, first_script, git_show, needs_node,
                     run_js, strip_topbar, topbar_script)

ROOT_STUBS = ["blis-design-3-pages.html", "blis-design-7-pages.html", "blis-target-design.html"]


def versioned_pages():
    return sorted(p for p in REPO.glob("v*/**/*.html") if "/src/" not in p.as_posix()
                  and re.fullmatch(r"v\d+\.\d+\.\d+", p.relative_to(REPO).parts[0]))


class TestSiteFiles(unittest.TestCase):
    def test_every_versioned_page_has_topbar_and_version_meta(self):
        pages = versioned_pages()
        self.assertGreaterEqual(len(pages), 4)
        for page in pages:
            html = page.read_text()
            folder = page.relative_to(REPO).parts[0][1:]
            m = TOPBAR_RE.search(html)
            self.assertIsNotNone(m, f"{page}: no top bar")
            self.assertIn("Design version", m.group(0), page)
            meta = re.findall(r'<meta name="blis-design-version" content="([^"]+)">', html)
            self.assertEqual(meta, [folder], f"{page}: version meta")
            self.assertTrue(m.start() == html.index("<body>") + len("<body>"),
                            f"{page}: top bar is not right after <body>")
            self.assertIn('<meta name="blis-design-version"', m.group(0),
                          f"{page}: meta must sit inside the markers")

    def test_versions_json_points_at_existing_folders(self):
        data = json.loads((REPO / "versions.json").read_text())
        listed = [v["version"] for v in data["versions"]]
        self.assertIn(data["latest"], listed)
        for entry in data["versions"]:
            folder = REPO / entry["path"]
            self.assertTrue(folder.is_dir(), entry)
            self.assertTrue(entry["path"].endswith("/"))
            self.assertEqual(entry["path"], f"v{entry['version']}/")
            self.assertTrue((folder / "index.html").is_file())

    def test_v1_copies_differ_from_tag_only_by_topbar(self):
        for name in PAGES:
            tagged = git_show("v1.0.0", name)
            copy = (REPO / "v1.0.0" / name).read_bytes()
            self.assertNotEqual(copy, tagged, name)
            restored = TOPBAR_RE.sub("", copy.decode(), count=1).encode()
            self.assertEqual(restored, tagged, f"{name}: removing the top bar must restore the tag")

    def test_topbar_fragment_is_theme_aware_and_not_sticky(self):
        frag = (REPO / "tools/site/topbar.html").read_text()
        self.assertIn("{{VERSION}}", frag)
        self.assertIn("prefers-color-scheme: dark", frag)
        self.assertIn("var(--", frag)
        self.assertNotRegex(frag, r"position\s*:\s*(sticky|fixed)")
        self.assertIn("@media print", frag)
        self.assertRegex(frag, r"flex-wrap\s*:\s*wrap")

    def test_readme_links_exist(self):
        readme = (REPO / "README.md").read_text()
        links = re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", readme)
        local = [l for l in links if not re.match(r"[a-z]+:", l)]
        self.assertTrue(local, "README should link to the pages")
        for link in local:
            self.assertTrue((REPO / link).exists(), f"README link does not resolve: {link}")
        # The versioned pages the README names must exist as files.
        for name in re.findall(r"`(v\d+\.\d+\.\d+/[\w.-]+\.html)`", readme):
            self.assertTrue((REPO / name).is_file(), name)


class TestRootPages(unittest.TestCase):
    def test_root_stubs_have_noscript_link_and_refresh_fallback(self):
        for name in ROOT_STUBS:
            html = (REPO / name).read_text()
            self.assertIn(f'v1.0.0/{name}', html)
            self.assertRegex(html, r'(?s)<noscript>.*?<a href="v1\.0\.0/' + re.escape(name))
            self.assertRegex(html, r'<meta http-equiv="refresh" content="0; ?url=v1\.0\.0/' + re.escape(name))
            self.assertLess(len(html), 2500, f"{name} should be a stub")

    def test_root_index_links_latest_version(self):
        data = json.loads((REPO / "versions.json").read_text())
        html = (REPO / "index.html").read_text()
        self.assertIn(f'href="v{data["latest"]}/index.html"', html)
        self.assertNotIn("http-equiv", html)

    @needs_node
    def test_root_stubs_redirect_with_hash(self):
        for name in ROOT_STUBS:
            html = (REPO / name).read_text()
            script = first_script(html)
            report = run_js(script, hash="#cov-8", href=f"https://h.example/blis-design/{name}#cov-8",
                            pathname=f"/blis-design/{name}")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["navigated"], [f"v1.0.0/{name}#cov-8"], name)
            plain = run_js(script, hash="", pathname=f"/blis-design/{name}")
            self.assertEqual(plain["navigated"], [f"v1.0.0/{name}"], name)

    @needs_node
    def test_root_index_redirects_only_when_versions_json_loads(self):
        script = first_script((REPO / "index.html").read_text())
        data = json.loads((REPO / "versions.json").read_text())
        ok = run_js(script, fetch="json", versions=data, pathname="/blis-design/")
        self.assertEqual(ok["errors"], [])
        self.assertEqual(ok["navigated"], [f"v{data['latest']}/index.html"])
        for mode in ("reject", "throw", "notok", "badjson", "absent"):
            bad = run_js(script, fetch=mode, versions=data, pathname="/blis-design/")
            self.assertEqual(bad["navigated"], [], mode)
            self.assertEqual(bad["errors"], [], mode)


class TestPicker(unittest.TestCase):
    def page_script(self, name="blis-target-design.html"):
        return topbar_script((REPO / "v1.0.0" / name).read_text())

    @needs_node
    def test_picker_survives_missing_versions_json(self):
        script = self.page_script()
        for mode in ("reject", "throw", "notok", "badjson", "absent"):
            report = run_js(script, meta="1.0.0", fetch=mode)
            self.assertEqual(report["errors"], [], mode)
            self.assertEqual([o["value"] for o in report["options"]], ["1.0.0"], mode)
            self.assertEqual(report["value"], "1.0.0", mode)

    @needs_node
    def test_picker_lists_versions_and_marks_current(self):
        versions = {"latest": "2.0.0", "versions": [
            {"version": "1.0.0", "path": "v1.0.0/"}, {"version": "2.0.0", "path": "v2.0.0/"}]}
        report = run_js(self.page_script(), meta="1.0.0", fetch="json", versions=versions)
        self.assertEqual([o["value"] for o in report["options"]], ["1.0.0", "2.0.0"])
        self.assertEqual(report["value"], "1.0.0")
        self.assertEqual(report["fetched"], ["../versions.json"])

    @needs_node
    def test_picker_navigates_with_hash(self):
        versions = {"latest": "2.0.0", "versions": [
            {"version": "1.0.0", "path": "v1.0.0/"}, {"version": "2.0.0", "path": "v2.0.0/"}]}
        page = "https://h.example/blis-design/v1.0.0/blis-target-design.html"
        report = run_js(self.page_script(), meta="1.0.0", fetch="json", versions=versions,
                        href=page + "#x", pathname="/blis-design/v1.0.0/blis-target-design.html",
                        hash="#x", choose="2.0.0")
        self.assertEqual(report["errors"], [])
        self.assertEqual(len(report["navigated"]), 1)
        self.assertEqual(urljoin(page + "#x", report["navigated"][0]),
                         "https://h.example/blis-design/v2.0.0/blis-target-design.html#x")

    @needs_node
    def test_picker_keeps_index_name_when_page_is_a_folder(self):
        versions = {"latest": "2.0.0", "versions": [
            {"version": "1.0.0", "path": "v1.0.0/"}, {"version": "2.0.0", "path": "v2.0.0/"}]}
        page = "https://h.example/blis-design/v1.0.0/"
        report = run_js(self.page_script("index.html"), meta="1.0.0", fetch="json", versions=versions,
                        href=page, pathname="/blis-design/v1.0.0/", choose="2.0.0")
        self.assertEqual(urljoin(page, report["navigated"][0]),
                         "https://h.example/blis-design/v2.0.0/index.html")

    @needs_node
    def test_picker_ignores_a_version_path_that_leaves_the_site(self):
        versions = {"latest": "2.0.0", "versions": [
            {"version": "1.0.0", "path": "v1.0.0/"}, {"version": "2.0.0", "path": "../../evil/"}]}
        report = run_js(self.page_script(), meta="1.0.0", fetch="json", versions=versions, choose="2.0.0")
        self.assertEqual(report["navigated"], [])
        self.assertEqual(report["errors"], [])


class TestNodeInCi(unittest.TestCase):
    def test_node_is_present_when_running_in_ci(self):
        import os
        from support import NODE
        if os.environ.get("CI"):
            self.assertIsNotNone(NODE, "CI must install Node so the JavaScript tests run")


if __name__ == "__main__":
    unittest.main()
