"""Helpers shared by the site tooling: the top bar and the root landing page."""
import json
import pathlib
import re

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
TOPBAR_RE = re.compile(r"<!--topbar-->.*?<!--/topbar-->", re.S)


def topbar_block(version, root=ROOT):
    """The top bar for one version, from tools/site/topbar.html, without a final newline."""
    text = (pathlib.Path(root) / "tools/site/topbar.html").read_text()
    return text.replace("{{VERSION}}", version).rstrip("\n")


def insert_topbar(html, version, root=ROOT):
    """Put the top bar right after <body>. strip_topbar undoes it byte for byte."""
    if "<!--topbar-->" in html:
        raise ValueError("page already has a top bar")
    if html.count("<body>") != 1:
        raise ValueError("page must contain exactly one <body>")
    return html.replace("<body>", "<body>" + topbar_block(version, root), 1)


def strip_topbar(html):
    return TOPBAR_RE.sub("", html, count=1)


def render_landing(versions, root=ROOT):
    """The root index.html: a static link to the latest version and a list of all versions."""
    latest = versions["latest"]
    entries = {v["version"]: v["path"] for v in versions["versions"]}
    items = "\n".join(
        f'<li><a href="{path}index.html">{version}</a></li>' for version, path in entries.items()
    )
    text = (pathlib.Path(root) / "tools/site/landing.html").read_text()
    return (text.replace("{{LATEST_PATH}}", entries[latest]).replace("{{LATEST}}", latest)
            .replace("{{VERSION_ITEMS}}", items))


def load_versions(root=ROOT):
    return json.loads((pathlib.Path(root) / "versions.json").read_text())
