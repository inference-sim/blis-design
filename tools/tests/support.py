"""Shared helpers for the site and build tests (standard library only)."""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

TESTS = pathlib.Path(__file__).resolve().parent
TOOLS = TESTS.parent
REPO = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

NODE = shutil.which("node")
PAGES = ["index.html", "blis-design-3-pages.html", "blis-design-7-pages.html", "blis-target-design.html"]

needs_node = unittest.skipUnless(
    NODE, "node is not installed: JavaScript behaviour tests are skipped here and run in CI"
)

TOPBAR_RE = re.compile(r"<!--topbar-->.*?<!--/topbar-->", re.S)


def strip_topbar(html):
    return TOPBAR_RE.sub("", html, count=1)


def topbar_script(html):
    """The script inside a page's top-bar markers."""
    block = TOPBAR_RE.search(html).group(0)
    return re.search(r"<script>(.*?)</script>", block, re.S).group(1)


def first_script(html):
    return re.search(r"<script>(.*?)</script>", html, re.S).group(1)


def run_js(script, **scenario):
    """Run `script` under Node with stubbed document, location and fetch.

    Scenario keys: href, pathname, hash, meta (version string or None),
    fetch ('reject', 'throw', 'json', 'notok', 'badjson', 'absent'),
    versions (the JSON a fetch resolves to), choose (value to select).
    Returns the harness's JSON report.
    """
    scenario["script"] = script
    done = subprocess.run(
        [NODE, str(TESTS / "harness.js")],
        input=json.dumps(scenario),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if done.returncode != 0:
        raise AssertionError("harness failed: " + done.stderr)
    return json.loads(done.stdout)


def git_show(ref, name):
    return subprocess.run(
        ["git", "show", f"{ref}:{name}"], cwd=REPO, capture_output=True, check=True
    ).stdout
