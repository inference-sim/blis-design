# blis-design v1.0.0, v2.0.0 and the versioned site: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tag today's design as v1.0.0, and publish a versioned design site with a version picker. Write
design v2.0.0 (the full design plus its three-page and seven-page summaries) from v1.0.0, adopting the M3.2
decisions. Put the design's source, build and checks into the repository.

**Architecture:** blis-design stays a static GitHub Pages site served from `main`. Each version lives in its own
folder. v1.0.0 is frozen built HTML. v2.0.0 is built from section sources in the repository by a small Python
script, which also adds the top bar. CI rebuilds and fails on any difference. A version picker in every page's top
bar reads `versions.json`.

**Tech stack:** HTML and CSS, standard-library Python 3 (no third-party packages, X21), GitHub Actions, git, `gh`.

**Spec:** `m32/design-v2-spec.md` on blis-design branch `m32-design-changes` (PR #36). The substance of v2.0.0 comes
from `m32/requirements.md` there: the Terms, DC1 to DC5, §1.4, §1.6, §2, §3.2, §3A and §3B.

## Global constraints

- v2.0.0 is a standing design: no dates, milestones, release counts, issue lists or "today" in its standing
  sections. `standcheck.py` enforces this.
- The writing bar: no AI flourishes; clear to the standard of Knuth, Lamport, Healy and Bostock; readable by
  engineers of every level. It must clear expert audits by top inference engineers and by discrete-event-simulation
  experts. Define every term at or before first use, use one name per concept, write short plain sentences with no
  intensifiers, and give each table and figure a caption that states its claim.
- The bar for implementations the design drives: maximise coverage, accuracy, fidelity to upstream, correctness and
  closeness grades. Check correctness with behavioural tests (conformance, differential, mutation, metamorphic,
  property), never structural ones.
- Rule IDs stay wherever a rule survives. Only rules made moot by DC1 to DC3 or by the blis-kvstore decision are
  retired. External KV stores (blis-kvstore, LMCache, Mooncake) are out of v2.0.0.
- British spelling (behaviour, modelled, licence).
- Commits are signed, with one `Assisted-by:` line and `Signed-off-by:`, and no `Co-Authored-By`. No private names:
  the M3.1 privacy-pattern scan stays clean.
- No new GPU or cluster experiments are described as required by any rule.
- The site works at phone width and in light and dark themes. Every page stays a single self-contained HTML file.

## Review focus

1. **An old link with an anchor**, such as `blis-target-design.html#cov-8`: it must land on the same anchor in
   `v1.0.0/`, not on the top of a page and not in v2.0.0. Tested in Task 2.
2. **A page opened from disk** (`file://`), where `versions.json` cannot be fetched: the picker must still show the
   current version and stay usable, not throw. Tested in Task 2.
3. **A source edited without a rebuild**: CI must fail and name the page. Tested in Task 3.
4. **A rule ID cited by an implementation that v2.0.0 renames or retires**: the appendix must list it with its fate,
   so a reader following an old ID finds where it went. Tested in Task 9.
5. **A standing section that picks up a date or a milestone** during editing: `standcheck.py` must fail. Tested in
   Task 3.

---

### Task 1: Tag v1.0.0

**Files:** none (git and GitHub only).

- [ ] **Step 1:** In the blis-design clone, confirm `main` is at `d4e5230` with `git log -1 --format=%h origin/main`.
  Expected: `d4e5230`.
- [ ] **Step 2:** Create a signed annotated tag:
  `git tag -s v1.0.0 d4e5230 -m "BLIS design v1.0.0: the standing design as of M3.1"`.
- [ ] **Step 3:** Push it and create the release:
  `git push origin v1.0.0 && gh release create v1.0.0 --verify-tag --title "BLIS design v1.0.0" --notes-file <notes>`.
  The notes say what v1.0.0 is and link the three pages.
- [ ] **Step 4:** Verify with `gh release view v1.0.0 -R inference-sim/blis-design --json tagName,targetCommitish`.

### Task 2: The versioned site, version picker and redirects

**Files:**
- Create: `v1.0.0/index.html`, `v1.0.0/blis-design-3-pages.html`, `v1.0.0/blis-design-7-pages.html`,
  `v1.0.0/blis-target-design.html`. These are today's root pages with the top bar inserted after `<body>`, and no
  other change.
- Create: `versions.json`. This is the list of versions and the latest one.
- Create: `tools/site/topbar.html`. The top bar's markup, style and script; the build inlines it.
- Modify: the root `index.html` into a landing page that opens the latest version and has the top bar.
- Modify: the root `blis-design-3-pages.html`, `blis-design-7-pages.html` and `blis-target-design.html` into
  redirect stubs to `v1.0.0/<same name>`, keeping `location.hash`, with a `<noscript>` link.
- Test: `tools/tests/test_site.py`.

**Interfaces:**
- Produces: `versions.json` = `{"latest": "2.0.0", "versions": [{"version": "2.0.0", "path": "v2.0.0/"},
  {"version": "1.0.0", "path": "v1.0.0/"}]}`. The top bar marks the current version by a
  `<meta name="blis-design-version" content="X.Y.Z">` in each page.
- Produces: `tools/site/topbar.html`, an HTML fragment with the placeholder `{{VERSION}}`.

Steps:
- [ ] **Step 1:** Write the failing tests:
  - `test_every_versioned_page_has_topbar_and_version_meta`: every `v*/**/*.html` contains the top-bar element and a
    version meta equal to its folder's version.
  - `test_versions_json_points_at_existing_folders`: each listed path exists, and `latest` is listed.
  - `test_root_stubs_redirect_with_hash`: each root stub's script sets `location.replace` to
    `v1.0.0/<name>` plus `location.hash`, and its `<noscript>` link targets the same file.
  - `test_v1_copies_differ_from_tag_only_by_topbar`: removing the top-bar element from each `v1.0.0/` page gives
    the bytes of that page at tag `v1.0.0` (read with `git show v1.0.0:<name>`).
  - `test_picker_survives_missing_versions_json`: the inline script wraps the fetch in try/catch and, on failure,
    renders the current version from the meta. Exercise it by running the script's `render` function under Node if
    it is available; otherwise check the fallback branch is present.
- [ ] **Step 2:** Run `python3 -I -m unittest tools/tests/test_site.py`. Expected: the tests fail, because the
  folders do not exist yet.
- [ ] **Step 3:** Create the files above. The picker is a `<select>` labelled "Design version", listing
  `versions.json`'s entries. Changing it navigates to the same file name in the chosen version, keeping the hash.
  All colours come from the pages' existing tokens. It works at 400 px width.
- [ ] **Step 4:** Run the tests. Expected: they pass.
- [ ] **Step 5:** Commit.

### Task 3: Build and checks in the repository, with CI

**Files:**
- Create: `tools/build.py`. `build(version: str) -> list[pathlib.Path]` builds `v<version>/*.html` from
  `v<version>/src/`, with `--check` to compare instead of write.
- Create: `tools/check.py` and `tools/standcheck.py`, ported from `.design-notes`, taking a page path.
- Create: `v2.0.0/src/`, seeded by splitting today's `blis-target-design.html` at each `<h2 id=...>` into
  `NN-<id>.html`, plus `style.css`, `head.html` and one source per summary (`summary-3.html`, `summary-7.html`).
- Create: `.github/workflows/design.yml`, which runs the tests, `build.py --check`, `check.py` and
  `standcheck.py` on every pull request.
- Test: `tools/tests/test_build.py`.

**Interfaces:**
- Consumes: `tools/site/topbar.html` (Task 2).
- Produces: `build("2.0.0")`, writing `v2.0.0/blis-target-design.html`, `v2.0.0/blis-design-3-pages.html`,
  `v2.0.0/blis-design-7-pages.html` and `v2.0.0/index.html`, each with the top bar and the version meta.

Steps:
- [ ] **Step 1:** Write the failing tests:
  - `test_seed_round_trips_v1`: before any v2 edit, building the seeded sources gives v1.0.0's full design,
    byte for byte apart from the top bar and the version meta.
  - `test_check_flags_stale_page`: after a source edit with no rebuild, `build.py --check` exits non-zero and names
    the page.
  - `test_standcheck_rejects_a_date_in_a_standing_section`: a fixture section containing `2026-11-19` fails, and
    the same text in §4.5 passes.
  - `test_toc_lists_every_section_in_order`.
- [ ] **Step 2:** Run them. Expected: they fail.
- [ ] **Step 3:** Implement `build.py`, port the checks, seed `v2.0.0/src/` and add the workflow.
- [ ] **Step 4:** Run the tests and `python3 -I tools/build.py 2.0.0 --check`. Expected: they pass.
- [ ] **Step 5:** Commit. CI runs green on the pull request.

### Task 4: README and the versioning rule

**Files:** Modify `README.md`.

- [ ] **Step 1:** Write the README:
  - what each page is, per version;
  - where the source is, and how to build and check it;
  - the semantic-versioning rule: MAJOR when a rule changes meaning or is removed, or the repository layout
    changes; MINOR when a rule or section is added that conforming implementations already satisfy or can adopt
    without breaking; PATCH for wording only;
  - tags are signed, annotated and never moved;
  - each release plan names the design version it implements;
  - how to add a version (a folder, `src/`, one line in `versions.json`).
- [ ] **Step 2:** Check the README links resolve on the built site (`test_site.py` gains `test_readme_links_exist`).
- [ ] **Step 3:** Commit.

### Tasks 5 to 9: Write v2.0.0's full design

Each task edits sources in `v2.0.0/src/`, rebuilds, runs `check.py` and `standcheck.py`, and commits. Each ends
with an independent read of its sections against the writing bar, with every finding fixed. Each keeps rule IDs
stable, and records every changed, merged or retired ID for Task 9's appendix. The substance comes from the `m32`
requirements and must not include their release-specific figures.

#### Task 5: Reading guide, shape and components (§1, §2, §3)

- §1: how to read the design, including the versioning rule and the component vocabulary.
- §2: one repository (inference-sim) plus the router fork. A new **component table** replaces the repository cards.
  For each component it gives what it owns, what it may import, what it must never contain, and the check that
  enforces it. The components are: contracts, catalog, coefficient registry, cost model, ledger, each engine module,
  the simulator, the router fork with its hosting contract, accuracy-dashboard and blis-config-search. Figure 1 is
  redrawn for the layout.
- §3: blis-substrate's four parts as packages (contracts, catalog, registry, cost model). Their import rules and
  the data rules (SUB-x) are kept; SUB-13 is restated for one module.

#### Task 6: Cross-cutting rules, components and the engine boundary (§4, §5, §6)

- §4: the X rules rewritten for one repository plus the fork.
  - X10 retires (there is no bottom-up merge).
  - X11 keeps its one replace.
  - X7 states that the fork depends on no BLIS module.
- §5: the per-component details that do not fit the table, including the router fork's ownership of the hosting
  contract (RTR-3 and SUB-1).
- §6: lowering lives only in engine modules (DC2), and the deriver writes checkpoint facts only (SUB-15). The
  boundary checks run on the import graph.

#### Task 7: Fidelity, simulation method and coefficients (§7, §8, §9)

- §7: an engine module models one upstream commit (DC1).
  - Engine upgrade and model support are distinct. A model backport is described.
  - The upgrade report is defined.
  - A new engine (for example TRT-LLM) meets the same bar: scheduling and KV code ported, and checked by an oracle
    that runs upstream code, through bindings for C++.
  - Behavioural testing is required throughout: conformance, differential, mutation, metamorphic and property
    tests.
- §8: the simulation method, written to clear discrete-event-simulation experts. It states the event model,
  virtual time, determinism and seeding, how events at the same time are ordered, the warm-up and the measured
  window, the independence assumptions, verification and validation, and how replications and confidence are
  reported.
- §9: the ranked coefficient methods (§9.2), the fallback guarantee (VAL-2), coefficients keyed by implementation,
  and engine-path costs keyed by the identity of the code that does the work (m32 §3.2).

#### Task 8: The ledger, accuracy coverage and procedures (§10, §11, §12)

- §10: data roles. Accuracy is reported only on held-out units. New sources carry training roles only. Roles are
  drawn per role key. A new data source joins the ledger continuously, with its run settings identified from its
  own records. No new GPU or cluster experiments.
- §11: grades G1 to G5 with commit distance (DC1). Coverage is reported as a funnel per scored source. Older runs
  count at their grade, and there is no age limit. Accuracy is sliceable by any recorded attribute, with the rule
  for small slices.
- §12: one **procedure** per recurring change: an engine upgrade, model support, onboarding a model, a new engine,
  a new data source, and a fidelity fix. Each has its trigger, the components it touches, its steps and a "done
  when". The `onboard --plan` command is removed: simulating the scenario and the upgrade report answer instead.

#### Task 9: Automation, versions and appendices (§13, §14, A, B, C)

- §13: CI per component directory with path filters; the release bot without the pin sequence.
- §14: versions. An engine module pins one upstream commit. inference-sim is the one tagged release. The design's
  own semantic versioning is stated.
- Appendix A: the rule index, regenerated.
- Appendix B: the glossary, merged with the m32 Terms that are standing.
- Appendix C (new): a table mapping every v1.0.0 rule ID to its fate in v2.0.0 (kept, changed, merged into X, or
  retired), with one line of reason each.
  - Test `test_appendix_c_covers_every_v1_id`: every ID in v1.0.0's Appendix A appears in Appendix C.
  - Test `test_every_v2_rule_is_indexed`: every ID used in v2.0.0's text is in its Appendix A.

### Task 10: The three-page and seven-page summaries of v2.0.0

**Files:** `v2.0.0/src/summary-3.html`, `v2.0.0/src/summary-7.html`, `v2.0.0/src/index.html`.

- [ ] **Step 1:** Rewrite both summaries from v2.0.0. Every claim links to the section of the full design that
  states it. The three-page summary is for a reader who knows llm-d and vLLM; the seven-page one is for a
  contributor about to change code.
- [ ] **Step 2:** Test `test_summary_links_resolve`: every `#anchor` link in the summaries exists in the full
  design.
- [ ] **Step 3:** Rebuild, run the checks, and commit.

### Task 11: Expert audits until clean

- [ ] **Step 1:** Run three independent, read-only audits of all of v2.0.0 in parallel. Each gets the spec and this
  plan's global constraints, and none sees the author's notes:
  - **inference engineers:** vLLM, SGLang, llm-d and NVIDIA serving. They check correctness of engine behaviour,
    fidelity, lowering, KV-cache and P/D statements, and the coefficient method.
  - **discrete-event-simulation experts:** the event model, time, ordering, determinism, warm-up, output analysis,
    and verification and validation.
  - **writing and consistency:** the writing bar, terms, cross-references, captions, contradictions, and the
    standing-design rule.
- [ ] **Step 2:** Fix every finding. Re-run any audit with material findings, until each reports none material.
- [ ] **Step 3:** Commit.

### Task 12: Pull request, release and m32

- [ ] **Step 1:** Open a pull request from `v2-design` to blis-design `main`, with the audit summary in its body.
  Ask the maintainer before merging.
- [ ] **Step 2:** After the merge, confirm on the live site that the picker switches versions, the old anchors
  redirect, and `latest` opens v2.0.0.
- [ ] **Step 3:** Ask the maintainer, then tag `v2.0.0` (signed, annotated) and create its release.
- [ ] **Step 4:** On the `m32` PR branch, mark section DC "adopted in design v2.0.0", and re-point the
  requirements' rule citations to v2.0.0's IDs.
