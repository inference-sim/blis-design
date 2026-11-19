# Work spec: blis-design v1.0.0, v2.0.0 and the versioned site

Agreed with the maintainer on 2026-11-19. This spec describes the work, not the design itself.

## Intent

The standing design must let BLIS evolve release after release without the cross-repository friction of M1 to
M3.1. v1.0.0 is today's design. v2.0.0 starts from v1.0.0 and builds in the M3.2 changes, while staying a standing
design: it holds across releases and contains no release planning, which stays on `m32` and in future release
plans. Together, v2.0.0 and the `m32` requirements must be enough to drive M3.2's implementation.

## The bar (maintainer)

The implementations the design drives must:
- maximise coverage, accuracy, fidelity to upstream and correctness;
- check correctness and invariants with behavioural tests (conformance, differential, mutation, metamorphic and
  property tests), never structural ones;
- deliver state-of-the-art accuracy for modelling and simulating inference performance;
- maximise the closeness grades (G1 to G5).

The text must meet the writing bar: no AI flourishes; clear to the standard of Knuth, Lamport, Healy and Bostock;
readable by engineers of every level. It must also clear expert audits by top inference engineers (vLLM, SGLang,
llm-d, NVIDIA) and by experts in discrete-event simulation. v2.0.0 must not be more complicated than v1.0.0, and should be simpler.

## What v2.0.0 must make easy, now and later

- An engine upgrade: blis-vllm to a new vLLM commit, blis-sglang to a new SGLang commit.
- A model, supported through one engine or both.
- A new engine, such as TRT-LLM, held to the same bar as vLLM and SGLang: its scheduling and KV-cache code is ported
  from upstream and checked by an oracle that runs the upstream code; the oracle may drive C++ code through its
  bindings.
- A new data source, with its run settings identified from its own records and its roles drawn by the ledger.
- Clean lowering, owned only by engine modules.
- Watertight separation of concerns between the components: the contracts, the catalog, the coefficient registry,
  the cost model, each engine module, the router fork with its hosting contract, the simulator, accuracy-dashboard
  and blis-config-search. The separation holds through consolidation, because it is
  enforced at package boundaries in CI rather than by repository walls.

## Decisions (adopted as decided; a later review may amend them)

1. **Tag v1.0.0** at blis-design `main` `d4e5230`, as an annotated tag, with a GitHub release.
2. **Versioned site.**
   - `v1.0.0/` holds today's pages, frozen: the content stays as tagged, and only a top bar is added.
   - `v2.0.0/` holds the new design.
   - The root page opens the latest version.
   - A version picker in each page's top bar reads `versions.json`. Adding a version later means one folder and
     one line.
   - GitHub Pages keeps serving `main` from the root.
3. **README.**
   - What each page is.
   - The semantic-versioning rule:
     - MAJOR when a rule changes meaning or is removed, or the repository layout changes;
     - MINOR when a rule or section is added that a conforming implementation already satisfies or can adopt
       without breaking;
     - PATCH for wording only.
   - Tags are annotated and never moved.
   - Each release plan names the design version it implements.
4. **Source in the repository.**
   - v2.0.0's source is one HTML file per section under `v2.0.0/src/`, with a shared stylesheet.
   - The build script and the checks (`check.py`, `standcheck.py`, a staleness check) live in the repository, and
     CI fails when the built page does not match its source.
   - v1.0.0 stays as its built pages.
5. **Content of v2.0.0, moulded from v1.0.0.**
   - It adopts DC1, DC2 and DC3 of the `m32` requirements:
     - DC1: engines model an upstream commit;
     - DC2: lowering lives only in engine modules;
     - DC3: blis-substrate, blis-vllm and blis-sglang move into inference-sim, and the hosting contract moves to
       the router fork.
   - It adds one procedure for each recurring change: an engine upgrade, model support, onboarding a model, a new
     engine, a new data source. Each gives its trigger, the components it touches, its steps and a "done when".
   - One component table gives, for each component, what it owns, what it may import, what it must never
     contain, and the check that enforces it. It replaces the per-repository cards.
   - It removes what consolidation makes moot: the cross-repository pin sequence, the bottom-up merge order, and
     per-engine release branches.
   - Rule IDs stay where a rule survives. An appendix maps every v1.0.0 rule ID to its fate in v2.0.0 (kept,
     changed, merged into another, or retired), so implementations can re-point.
   - The data rules adopt what the `m32` requirements decided, as standing rules:
     - accuracy is reported only on held-out units;
     - new sources carry training roles only;
     - no new GPU or cluster experiments: a missing measurement is priced by the most trusted fallback (design
       §9.2), and the point names it;
     - each run's settings come from its own records.
   - Release-specific content (dates, counts, milestones) stays out, as `standcheck.py` enforces.
6. **Summaries (maintainer, 2026-11-19).** v2.0.0 keeps all three documents, as v1.0.0 has them: the design in three
   pages, the design in seven pages, and the full design. Each is rewritten from v2.0.0 and held to the same bar.
7. **Checks before release.**
   - Independent audits against both bars, including one from the stance of top inference engineers and one from
     the stance of discrete-event-simulation experts.
   - A pull request to blis-design `main`.
   - The maintainer is asked before that pull request merges, and before v2.0.0 is tagged.
8. **`m32`.** Section DC becomes "adopted in design v2.0.0", and the requirements cite v2.0.0's rule IDs.

## Calls made after the builder check (2026-11-19)

These settle the questions a builder would otherwise have to guess. Each is the author's call, open to the
maintainer's correction in the pull request.

1. **Who writes v2.0.0.** It is written, not assembled: v1.0.0's prose, edited to adopt DC1 to DC3 and the data
   rules, plus the new procedures, the component table and the rule-ID appendix. DC1 to DC3 in the `m32`
   requirements supply the substance. The independent audits run on the whole of v2.0.0, once it is written.
2. **Rule-ID fates.**
   - A rule is retired only when DC1 to DC3 or the decision on external KV-cache providers make it moot.
   - Every other rule is kept, or reworded where its meaning must change.
   - The appendix records each one's fate, and the maintainer reviews it in the pull request.
3. **Checks and layout.**
   - `build.py`, `check.py` and `standcheck.py` move into the repository, under `tools/`, adapted to
     `v2.0.0/src/`.
   - They run on v2.0.0 only. v1.0.0 is frozen and not re-checked.
   - The staleness check compares each built v2.0.0 page with its sources.
   - The top bar is added to v2.0.0's pages by the build, and once, by hand, to the v1.0.0 copies.
4. **v1.0.0 and its URLs.**
   - The tag records v1.0.0's content. The copies in `v1.0.0/` differ from it only by the top bar.
   - All three v1.0.0 pages move into `v1.0.0/`.
   - The old root URLs stay as redirect stubs to their v1.0.0 copies, keeping the `#anchor`. Repository READMEs
     and pull requests cite those URLs for the rules they were written against.
   - The root `index.html` opens the latest version. New citations use versioned URLs.
5. **The three-page and seven-page summaries.** Both are rewritten from v2.0.0, with their sources in
   `v2.0.0/src/`, and the same checks apply.
6. **No transition text.** v2.0.0 states the consolidated layout as the standing rule. Which design version a
   release implements is the release plan's business, as the README's versioning rule says. So v2.0.0 carries no
   transition note.
7. **Findings after approval.** If an audit finds a defect after the maintainer has approved, it is fixed, and
   approval is asked again.

## Left to the builder

- The order of sections in v2.0.0, provided it keeps v1.0.0's numbering wherever a section survives.
- The look of the top bar and the version picker, provided it works at phone width and in both themes.
- How v1.0.0's built page is split back into section sources for v2.0.0.

## Non-goals

- No design for external KV-cache providers: they stay out of v2.0.0, and a later
  MINOR version can add it (maintainer, 2026-11-19).

- No release planning in the design: no dates, milestones, counts or issue lists.
- No change to v1.0.0's content.
- No new tooling beyond the build, the checks and the version picker.
