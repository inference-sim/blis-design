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

## Decided (binding on every task)

- **Open questions of DC, settled as the author's calls under the maintainer's "adopt everything":**
  - Q1: a maintainer with write access decides an on-demand engine upgrade, recorded in an issue. There is no
    CODEOWNERS file (maintainer, 2026-11-19).
  - Q2: a model backport has no grade of its own; it is graded by commit distance.
  - Q3: `contracts/rules/` is removed together with the lowering move.
  - Q4: the three repositories are consolidated.
  - Q5 (DC4) is release content and stays out of the design.
- **Sources of substance:**
  - DC1 to DC3, as rules;
  - DC5, as the coverage checklist;
  - m32 §1.4, §1.6 and §3.2, as rules.
  - DC4, and every figure, count, scenario name and `M3.x` label of the m32 text, stay out. Internal scenarios are
    described generically.
- **Rule IDs:**
  - Prefixes survive the consolidation (SUB-, VLM-, SGL-, RTR-, and the rest).
  - The candidate retirements are X10 (bottom-up merge), the KVS family (external KV-cache providers are out), and any rule whose
    only subject is the cross-repository pin sequence or per-engine release branches.
  - Any other change is "changed" or "merged", never "retired".
- **Simplicity gate:** v2.0.0's full design has no more defined rule IDs, top-level sections or kilobytes than
  v1.0.0's (`check.py` prints the kilobytes). Any excess is justified line by line in the pull request.
- **One home for each fact:**
  - The component table is the one place for ownership and imports; the rules cite it.
  - The table replaces §5's repository cards; it does not sit beside them.
  - The design's own versioning rule is stated once, in the README; the design links to it.
- **Seed layout:** the source files hold section bodies only. The build emits the head, the generated table of
  contents, `<main>` and the closing tags. The seed starts from `/Users/sri/Documents/Projects/.design-notes`
  (`part1..6.html`, `style.css`, `build.py`, `check.py`, `standcheck.py`), brought up to date with `main` by
  splitting today's built page.
- **The top bar:**
  - It is wrapped in `<!--topbar-->` and `<!--/topbar-->` marker comments, and the version meta sits inside the
    markers, so removing the fragment restores a page byte for byte.
  - It is not sticky, so v1.0.0's sticky table of contents is unaffected.
- **`versions.json`** lists only versions that exist on `main`. Task 2 ships `latest: 1.0.0` with one entry, and
  Task 12 adds 2.0.0 when it merges.
- **The root `index.html`** is static: a link to the latest version, written by the build. It redirects only when
  `versions.json` loads.
- **Tag:** `git tag -s` (the maintainer's SSH signing is configured), annotated.
- **CI:**
  - It checks out with `fetch-depth: 0`, so tags are present.
  - It requires Node, which runs the picker and redirect scripts in behavioural tests. A test never falls back to
    checking that code is present.
  - It runs the M3.1 privacy-pattern scan.

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
- Rule IDs stay wherever a rule survives. Only rules made moot by DC1 to DC3 or by the decision on external KV-cache providers are
  retired. External KV-cache providers are out of v2.0.0.
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

### Task 0: Branch

- [ ] After Task 1's tag exists, create branch `v2-design` from `main` at `d4e5230`, in a worktree
  `blis-design-wt-v2`. Tasks 2 to 11 commit there.

### Task 1: Tag v1.0.0

**Files:** none (git and GitHub only).

- [ ] **Step 1:** In the blis-design clone, confirm `main` is at `d4e5230` with `git log -1 --format=%h origin/main`.
  Expected: `d4e5230`.
- [ ] **Step 2:** Create a signed, annotated tag:
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
- Produces: `versions.json` = `{"latest": "1.0.0", "versions": [{"version": "1.0.0", "path": "v1.0.0/"}]}`
  (Task 12 adds 2.0.0). The top bar marks the current version by a
  `<meta name="blis-design-version" content="X.Y.Z">` in each page.
- Produces: `tools/site/topbar.html`, an HTML fragment with the placeholder `{{VERSION}}`.

Steps:
- [ ] **Step 1:** Write the failing tests:
  - `test_every_versioned_page_has_topbar_and_version_meta`: every `v*/**/*.html` contains the top-bar element and a
    version meta equal to its folder's version.
  - `test_versions_json_points_at_existing_folders`: each listed path exists, and `latest` is listed.
  - `test_root_stubs_redirect_with_hash`: run each root stub's script under Node with a stub `location`
    (`hash = "#cov-8"`), and assert that it navigates to `v1.0.0/<name>#cov-8`.
  - `test_v1_copies_differ_from_tag_only_by_topbar`: removing the top-bar element from each `v1.0.0/` page gives
    the bytes of that page at tag `v1.0.0` (read with `git show v1.0.0:<name>`).
  - `test_picker_survives_missing_versions_json`: run the picker script under Node with a `fetch` that rejects,
    and assert that it renders one option, equal to the page's version meta, and throws nothing.
  - `test_picker_navigates_with_hash`: with `versions.json` loaded and the page at `v1.0.0/blis-target-design.html#x`,
    choosing 2.0.0 navigates to `v2.0.0/blis-target-design.html#x`.
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
  `NN-<id>.html` (section bodies only), plus `style.css`, `head.html`, one source per summary (`summary-3.html`,
  `summary-7.html`, seeded from v1.0.0's) and `index.html` (seeded from v1.0.0's). The meta description is
  rewritten so that it holds no release wording.
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
  - `test_standcheck_rejects_release_content`: a fixture section containing a bare date (`2026-11-19`), an
    `M3.2` label, or a sentence of the form "until a MINOR version adds" fails. The same section with a trigger test
    ID (`T-E1`) passes. The check also scans the page's meta description.
  - `test_toc_matches_source_order`: the table of contents lists the sections in the order of the `src/` file
    names, which matches v1.0.0's order for every section that survives.
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

- §10: data roles. A measurement no source has is priced by the most trusted fallback (§9.2), and the point names
  its method. Accuracy is reported only on held-out units. New sources carry training roles only. Roles are
  drawn per role key. A new data source joins the ledger continuously, with its run settings identified from its
  own records. No new GPU or cluster experiments.
- §11: grades G1 to G5 with commit distance (DC1). Coverage is reported as a funnel per scored source. Older runs
  count at their grade, and there is no age limit. Accuracy is sliceable by any recorded attribute, with the rule
  for small slices.
- §12: one **procedure** per recurring change: an engine upgrade, model support, onboarding a model, a new engine,
  a new data source, and a fidelity fix (v1.0.0's §12 already has the last; the spec's five are the new or reworked
  ones). Each has its trigger, the components it touches, its steps and a "done
  when". The `onboard --plan` command is removed: simulating the scenario and the upgrade report answer instead.

#### Task 9: Automation, versions and appendices (§13, §14, A, B, C)

- §13: CI per component directory with path filters; the release bot without the pin sequence.
- §14: versions. An engine module pins one upstream commit. inference-sim is the one tagged release. Per-engine
  release branches (LIF-2, LIF-4, LIF-5, LIF-6, §14.4) give way to inference-sim's release branches. The design's
  own versioning links to the README, which is the one place it is stated.
- Appendix A: the rule index, regenerated.
- Appendix B: the glossary, merged with the m32 Terms that are standing.
- Appendix C (new): a table mapping every v1.0.0 rule ID to its fate in v2.0.0 (kept, changed, merged into X, or
  retired), with one line of reason each.
  - Appendix A is edited by hand; there is no generator.
  - Test `test_appendix_c_covers_every_v1_id`: every ID defined in v1.0.0 (each `<span class="inv">`, as
    `check.py` reads them, with ranges expanded) has one row in Appendix C. Each fate is one of kept, changed,
    merged or retired. A "merged into" names an ID defined in v2.0.0. Every "retired" ID is in the candidate list
    under Decided.
  - Test `test_every_v2_rule_is_indexed`: every ID defined in v2.0.0's text is in its Appendix A.
  - Test `test_v2_is_not_larger_than_v1`: defined rule IDs, top-level sections and kilobytes are each at most
    v1.0.0's, or the excess is listed in `tools/size-exceptions.txt` with its reason.

### Task 10: The three-page and seven-page summaries of v2.0.0

**Files:** `v2.0.0/src/summary-3.html`, `v2.0.0/src/summary-7.html`, `v2.0.0/src/index.html`.

- [ ] **Step 1:** Rewrite both summaries from v2.0.0. Every claim links to the section of the full design that
  states it. The three-page summary is for a reader who knows llm-d and vLLM; the seven-page one is for a
  contributor about to change code.
- [ ] **Step 2:** Test `test_summary_links_resolve`: every `#anchor` link in the summaries exists in the full
  design, and every link targets `v2.0.0/blis-target-design.html`, not v1.0.0.
- [ ] **Step 3:** Rebuild, run the checks, and commit.

### Task 11: Expert audits until clean

- [ ] **Step 1:** Run three independent, read-only audits of all of v2.0.0 in parallel. Each gets the spec and this
  plan's global constraints, and none sees the author's notes:
  - **inference engineers:** vLLM, SGLang, llm-d and NVIDIA serving. They check correctness of engine behaviour,
    fidelity, lowering, KV-cache and P/D statements, and the coefficient method. They also check that the rules
    require the implementation bar: maximal coverage, accuracy, fidelity and closeness grades, and behavioural
    testing.
  - **discrete-event-simulation experts:** the event model, time, ordering, determinism, warm-up, output analysis,
    and verification and validation.
  - **writing and consistency:** the writing bar, terms, cross-references, captions, contradictions, and the
    standing-design rule.
- [ ] **Step 2:** Check coverage of M3.2. Each DC1 to DC3 statement, and each row of DC5's table, lands in a named
  v2.0.0 rule or procedure. Record the mapping in the pull request.
- [ ] **Step 3:** Check the site at 400 px width and in both themes (an audit item, not a test).
- [ ] **Step 4:** Fix every finding. Re-run any audit with material findings, until each reports none material.
- [ ] **Step 3:** Commit.

### Task 12: Pull request, release and m32

- [ ] **Step 1:** Open a pull request from `v2-design` to blis-design `main`, with the audit summary in its body.
  Ask the maintainer before merging.
- [ ] **Step 2:** After the merge, confirm on the live site that the picker switches versions, the old anchors
  redirect, and `latest` opens v2.0.0.
- [ ] **Step 3:** Ask the maintainer, then tag `v2.0.0` (signed, annotated) and create its release.
- [ ] **Step 4:** On `m32-design-changes` (PR #36 into `m32`, the review route the maintainer asked for), mark
  section DC "adopted in design v2.0.0", and re-point the requirements' rule citations to v2.0.0's IDs. The `m32`
  branch is changed only through that PR.
