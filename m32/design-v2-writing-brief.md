# Writing brief for design v2.0.0

Every writer of v2.0.0 reads this brief, the plan (`m32/design-v2-plan.md`, especially "Decided"), the spec
(`m32/design-v2-spec.md`), and the Terms and section DC of `m32/requirements.md`. v1.0.0 is the starting text;
v2.0.0 is v1.0.0 edited, not a new document.

## Where the text lives

- Worktree: `/Users/sri/Documents/Projects/blis-design-wt-v2`, branch `v2-design`.
- Sources: `v2.0.0/src/NN-sN.html`, one per top-level section (section bodies only). The build adds the frame.
- Build: `python3 -I tools/build.py 2.0.0`. Check: `python3 -I tools/check.py v2.0.0/blis-target-design.html` and
  `python3 -I tools/standcheck.py v2.0.0/blis-target-design.html`.
- Each writer works in their own worktree, branched from `v2-design`, and edits only their own source files.

## What v2.0.0 changes, as standing rules

- **One repository and the router fork (DC3).**
  - blis-substrate, blis-vllm and blis-sglang become directories of inference-sim, in one Go module.
  - The router fork stays a separate repository. It owns the hosting contract (`contracts/embed` and its
    conformance suite) and depends on no BLIS module.
  - accuracy-dashboard and blis-config-search stay separate, and pin inference-sim releases.
  - blis-kvstore and external KV stores (LMCache, Mooncake) are out of v2.0.0. A later MINOR version may add them.
    Do not write a transition note about this; write as if they were never in scope. The one exception is
    Appendix C, which records each retired rule.
- **Engines model an upstream commit (DC1).**
  - A commit is a release tag or any upstream commit.
  - The engine upgrade and model support are distinct.
  - A model backport is model code only, and is graded by commit distance.
  - A maintainer with write access decides an on-demand upgrade, recorded in an issue.
  - Each upgrade generates an upgrade report.
  - A run on the modelled commit counts as the same build for grading (G1 or G2 possible).
- **Lowering lives only in engine modules (DC2).**
  - The catalog's deriver writes checkpoint facts only (SUB-15).
  - `contracts/rules/` is removed.
  - There is no onboarding preflight command: simulating the requested scenario, and the upgrade report, answer
    the same questions.
- **Every engine meets the same bar.** A new engine (for example TRT-LLM) ports its scheduling and KV-cache code
  from upstream, checked by an oracle that runs upstream code, through bindings for C++.
- **Coefficients.**
  - Kernel coefficients are keyed by kernel implementation.
  - Engine-path costs (host, scheduler, launch, CUDA-graph replay) are keyed by the identity of the code that does
    the work. No engine name appears in substrate (X2).
  - Every lookup falls back to the most trusted entry for the chip (§9.2), down to a roofline or an assumed entry
    (VAL-2), and the point names the method. New entries are required only for a new primitive family.
- **Data.**
  - Accuracy is reported only on held-out units (held and anchor).
  - Sources that are not held out are training data.
  - A new source draws training roles only.
  - Roles are drawn per role key.
  - Each run's settings come from its own records; a value no record holds is a named substitution.
  - No new GPU or cluster experiments.
  - There is no age limit on scoring.
  - Coverage is reported as a funnel per scored source.
  - Accuracy is sliceable by any recorded attribute. Below `min_points` no aggregate is shown.
- **Review.** Maintainers with write access decide on pull requests. There is no CODEOWNERS file, and v2.0.0 must
  not require one.
- **Testing.** Correctness and invariants are checked by behavioural tests: conformance, differential, mutation,
  metamorphic and property tests. Never structural tests, such as tests of source text, order, hashes or goldens
  used as a shortcut.

## The component table (owned by the §2 writer; everyone cites it)

It lives in §2.2, anchor `#s2-2`, as "Table 1. Components". Its columns are:
- component;
- what it owns;
- what it may import;
- what it must never contain;
- the check that enforces it.

The components and where they live. Each moved repository keeps its own tree, under one top-level directory of
inference-sim, so that paths inside it do not change:

- `substrate/`, formerly blis-substrate, keeps its tree:
  - `substrate/contracts/`: the shared types and interfaces, importing only the standard library and the YAML
    parser (SUB-1). Two of its packages leave. `contracts/embed` and `contracts/conformance/embedtest` move to the
    router fork. `contracts/kvstore` and `contracts/conformance/kvstoretest` retire with blis-kvstore.
  - `substrate/catalog/`: checkpoint and vendor facts, and the graph deriver.
  - `substrate/catalog/ledger/`: the units and roles of every data source.
  - `substrate/registry/`: coefficients, written only by their family's writer scripts.
  - `substrate/kernel/`: the cost model. It prices a fully lowered step and imports no engine.
  - `substrate/validate/` and `substrate/load/`: validators, and the data loader.
- `engines/vllm/` and `engines/sglang/`, formerly blis-vllm and blis-sglang: one directory per engine, each with its
  port, lowering, defaults and oracle. No engine imports another. A new engine is a new directory under `engines/`.
- The simulator stays where it is in inference-sim (`sim/`, `cmd/`). It reaches engines only through the engine
  contract, at one build site.
- The router fork (a separate repository): llm-d's router, and the hosting contract with its conformance suite.
- accuracy-dashboard (a separate repository): scoring and published accuracy.
- blis-config-search (a separate repository): configuration search.

## Rule IDs

- Keep every rule's ID and prefix (SUB-, VLM-, SGL-, RTR-, SIM-, FID-, DEV-, VAL-, COV-, D, CFG-, LIF-, X, T-).
- Retire only these:
  - X10;
  - the KVS family;
  - any rule whose only subject is the cross-repository pin sequence or per-engine release branches.
- Any other change is "changed" (the meaning changes) or "merged into <ID>".
- A new rule takes the next free number in its family.
- Record every ID you change, merge, retire or add in `v2.0.0/src/_idmap/<your-section-range>.tsv`, with the
  columns `v1_id`, `fate` (kept, changed, merged, retired or new), `v2_id` and `reason` (one line). Rows for kept
  IDs are optional.

## Simpler, not longer

- Remove what consolidation makes moot. Do not add a paragraph where a table row will do.
- Do not restate a rule that another section owns; cite its ID.
- The whole of v2.0.0 must not exceed v1.0.0 in defined rule IDs, top-level sections or kilobytes. Aim to be
  smaller.

## Writing bar

- No AI flourishes.
- Clear to the standard of Knuth, Lamport, Healy and Bostock. Readable by engineers of every level.
- It must clear audits by top inference engineers and by discrete-event-simulation experts.
- Define every term at or before first use (Appendix B is the glossary), and use one name per concept.
- Write short, plain sentences, without intensifiers, "not X but Y" rhetoric, em-dash asides or scare quotes.
- Every table and figure has a caption that states its claim.
- Use British spelling.
- Keep the text standing: no dates, milestones, counts from a snapshot, release labels (`M3.2`), issue lists or
  "today".
- No private names, and no names of internal scenarios.
- Cite upstream code at a pinned commit, as v1.0.0 does.
