# BLIS design

The BLIS design, in versions. The site is static and is served from `main` at
https://inference-sim.github.io/blis-design/. Every page is a single self-contained HTML file, and every page has a
top bar with a "Design version" picker that opens the same page in another version.

## Pages, per version

Each version has its own folder, and each folder holds the same four pages.

| Page | What it is |
| --- | --- |
| `index.html` | Where to start: the three documents in reading order. |
| `blis-design-3-pages.html` | The design in three printed pages, for a reader who already knows llm-d and vLLM. |
| `blis-design-7-pages.html` | The design in seven printed pages, for a contributor about to change code. |
| `blis-target-design.html` | The full design. It is the authority; the two summaries link to the sections that state each claim. |

The versions:

- [`v1.0.0/`](v1.0.0/index.html) is frozen. Its pages are the pages at tag `v1.0.0` plus the top bar, and nothing else
  changed. Its full design is [`v1.0.0/blis-target-design.html`](v1.0.0/blis-target-design.html).
- [`v2.0.0/`](v2.0.0/index.html) is frozen. Its sources stay in `v2.0.0/src/`, and its pages still rebuild from
  them unchanged.
- [`v2.1.0/`](v2.1.0/index.html) is the latest. It is built from the sources in `v2.1.0/src/`. Its full design is
  [`v2.1.0/blis-target-design.html`](v2.1.0/blis-target-design.html).

A new version starts as a copy of the latest version's `src/` in a new folder, plus one line in `versions.json`.

`versions.json` lists the versions that are published and names the latest. The root `index.html` links to the
latest version. The root `blis-design-3-pages.html`, `blis-design-7-pages.html` and `blis-target-design.html` are
redirects to `v1.0.0/`, so an old link, anchor included, still lands on the same text.

## Source, build and checks

Only the standard library of Python 3 is needed. Run these from the repository root.

```
python3 -I tools/build.py 2.1.0            # write v2.1.0/*.html from v2.1.0/src/
python3 -I tools/build.py 2.1.0 --check    # fail, naming the page, if a built page is stale
python3 -I tools/build.py --landing        # write the root index.html from versions.json
python3 -I tools/check.py v2.1.0/blis-target-design.html       # anchors, nesting, section and rule references
python3 -I tools/standcheck.py v2.1.0/blis-target-design.html  # no dates, milestones or release wording
python3 -m unittest discover -s tools/tests                    # tests
```

The sources of a version are in its `src/` folder:

- `head.html` and `style.css` hold the head of the full design.
- `00-front.html` holds its title and abstract. `NN-<id>.html` holds one section each. The build lists them in
  file-name order and generates the table of contents from their `<h2 id="...">` headings. `footer.html` closes the page.
- `summary-3.html`, `summary-7.html` and `index.html` hold the bodies of the other three pages, each with a
  `<name>.head.html`.
- A file or folder whose name starts with an underscore is a working note. The build ignores it.

Edit a source, run the build, and commit the sources and the built pages together. CI rebuilds with `--check` and
fails on any difference. It also runs the tests, `check.py` and `standcheck.py`, and a scan for private names. The
JavaScript tests for the version picker and the redirects need Node. They are skipped on a machine without it, and CI
installs it.

A page must not hold a date, a milestone label, an issue number or a statement about the current release. Those belong
to a release plan, not to the design.

## Version numbers

The design has a version of the form MAJOR.MINOR.PATCH.

- MAJOR changes when a rule changes meaning or is removed, or when the repository layout changes.
- MINOR changes when a rule or section is added that conforming implementations already satisfy or can adopt without
  breaking.
- PATCH changes for wording only.

A release is a tag `vMAJOR.MINOR.PATCH`. Tags are signed and annotated, and a tag is never moved. If a published
version is wrong, publish the next one. Each release plan names the design version it implements.

## Adding a version

1. Create the folder `vX.Y.Z/` with a `src/` folder that has the files listed above. Copy them from the previous
   version, then edit.
2. Build it with `python3 -I tools/build.py X.Y.Z`.
3. Add one line to `versions.json` and, if it is the newest, set `latest`. Then run `python3 -I tools/build.py --landing`.
4. Add the version to the workflow's build and check steps in `.github/workflows/design.yml`.
5. Open a pull request. After it merges, tag the merge commit `vX.Y.Z` (signed, annotated) and create the release.
