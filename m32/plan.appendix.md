## Plan decisions, now in the requirements

The decisions first drafted in this plan now live in the requirements, which are authoritative: the rule for small
slices (§3B), roles drawn per role key (§1.4), the calibration acceptance gates (§1.5, a proposal whose thresholds
are still to be set), and what becomes of blis-config-search#110 (§0.5). This section only points to them, so the
plan holds no decision the requirements do not.

## Prerequisites, to start now

- **Archive the sources that expire.** SGLang's nightly job logs and `consolidated-metrics` artifacts are kept
  about 90 days. Begin the pinned private archive now, so their history keeps growing instead of rolling off before
  M3.2 starts (§4.1). Tritonbench (90 days) and SGLang's AMD P/D artifacts (30 days) join it if §1.3 brings them in.
- **No new GPU or cluster runs, with no exceptions (§1.6).** The test of CPU-load completion steps
  (blis-vllm#305) uses runs already recorded. The GB200 custom all-reduce (blis-substrate#116) stays transferred
  until a source measures it (§0.6).

## Execution: ownership and order

These are still requirements, not yet an executable plan. The carried M3.1 issues are listed in
[`m31-carried.tsv`](m31-carried.tsv), but the M3.2 work needs an ordered sequence of pull requests. Table W gives
the workstreams in dependency order; pull-request numbers are assigned when the plan is made.

**Table W. Eighteen workstreams in dependency order; rows 1 to 4 and 18 build section DC and the design changes,
and once row 1 lands, a row that names blis-substrate, blis-vllm or blis-sglang is done in inference-sim.**

| # | Workstream | Owner repositories | Depends on rows |
|---|---|---|---|
| 1 | Migration: the hosting contract to the router fork; blis-substrate, blis-vllm and blis-sglang into inference-sim with history; issue transfer; checks; retire the three repositories (DC3, Table DC) | the three repositories, inference-sim, the router fork | a sizing first |
| 2 | Engines model an upstream commit: generators at any commit, the upgrade report, commit distance in grading, model backports (DC1, Table DC) | blis-vllm, blis-sglang, accuracy-dashboard | 1 |
| 3 | Lowering out of the graph deriver; `contracts/rules/` removed (DC2, Table DC) | blis-substrate, blis-vllm, blis-sglang | 1 |
| 4 | Mistral-Large-4 and Inkling-2-Small on GB200: engine upgrade, catalog entries, model support, coefficients (DC4) | blis-vllm, blis-substrate | 2 |
| 5 | Engine-path coefficients keyed by the identity of the code that does the work: `CodeID`, `code_paths.json`, `host_cpu` (§3.2, Table DC) | blis-substrate | none; no issue or pull request yet, and it gates every per-engine cost |
| 6 | Ingestion: the ledger follows each source, and the dump is reconciled with the API (§3A.1, §3A.9) | blis-substrate | none |
| 7 | Archive of the sources that expire (start now) | blis-substrate | none |
| 8 | The new calibration sources ingested, with training-only roles (§1, §1.4) | blis-substrate | 6, 7 |
| 9 | Count of anchor units whose inputs can be recovered, without simulating (§3A.8) | accuracy-dashboard | none; before the plan |
| 10 | Engine and table coverage: SGLang field list, router table, the settings no engine module models (§3A.4) | blis-sglang, blis-vllm, inference-sim, blis-substrate | 5 |
| 11 | Scoring: no age limit, commit distances (DC1), funnels for InferenceX and configiq (§3A.2, §3A.5, §3A.6) | accuracy-dashboard | 6, 9 |
| 12 | configiq as a ledger source: the rule for each writer, and a pinned revision (§3C) | blis-substrate, accuracy-dashboard | 6 |
| 13 | Calibration acceptance gates fixed in advance, and roles drawn per role key (§1.4, §1.5) | blis-substrate | 5, 8; before any fit |
| 14 | Dashboard: slicing by any attribute, and the rule for small slices (§3B) | accuracy-dashboard | 11 |
| 15 | blis-config-search#110's four successor workstreams (§0.5) | blis-config-search | only the first depends on 10 |
| 16 | CI: editing a pull request's text must not change its merge state (§5) | each repository's `ci.yml` (inference-sim's after row 1) | none |
| 17 | The 150 open M3.1 issues (§0.4), each taken into the row its plan item matches | as listed in `m31-carried.tsv` | per row |
| 18 | Simplifications of design v2.1.0: the `ledger`, `invariants` and `compose` commands removed, the ledger no longer embedded, the gated-config nightly deleted with its environment and secret, the gated-model step in the catalog README and PR template, the stale dashboard comment (Table DC) | inference-sim, blis-substrate, accuracy-dashboard | none; after row 1, the substrate part is done in inference-sim |

Row 13's gates must be written and merged before any fitting reads the new sources (VAL-6: the split and success
criteria are committed first). Row 5 has no design issue or pull request yet and blocks every per-engine cost, so it is
filed first.
