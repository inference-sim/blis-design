## Execution: ownership and order

These are still requirements, not yet an executable plan. The carried M3.1 issues are listed in
[`m31-carried.tsv`](m31-carried.tsv), but the M3.2 work needs an ordered sequence of pull requests. Table W gives
the workstreams in dependency order; pull-request numbers are assigned when the plan is made. Row 11 (archive the
expiring sources) starts now. Row 6 has no issue or pull request yet and gates the engine-path costs of rows 9, 15 and
18, so it is filed first.

**Table W. Twenty-four workstreams in dependency order. Every group of Table DC has a row (rows 1 to 8), a
dependency cell holds row numbers only, and once row 2 lands, a row that names blis-substrate, blis-vllm or blis-sglang
is done in inference-sim.**

| # | Workstream | Owner repositories | Depends on rows | Done when |
|---|---|---|---|---|
| 1 | Size the migration from the actual workflows, checks and open issues (Table DC, Sizing) | inference-sim, blis-substrate, blis-vllm, blis-sglang, the router fork | none | a list of workflows, checks and open issues per repository, and the pull-request sequence for rows 2, 3 and 5, is published |
| 2 | Migration: the hosting contract to the router fork; blis-substrate, blis-vllm and blis-sglang into inference-sim with history; issue transfer; checks; retire the three repositories (DC3, Table DC) | the three repositories, inference-sim, the router fork | 1 | the three repositories are archived and inference-sim's CI runs their checks by directory |
| 3 | Engines model an upstream commit: generators at any commit, the upgrade report, commit identity, commit distance in grading, model backports (DC1, Table DC) | blis-vllm, blis-sglang, accuracy-dashboard | 2 | a run on another commit is graded by its commit distance, and an upgrade report is generated |
| 4 | The vLLM and SGLang particulars of Table DC (tuned MoE configuration, defaults at two commits, platform preferences, KV events, step boundary, backport paths, P/D allocation, radix-tree core, surface lists); the TensorRT-LLM sites are recorded, not built | blis-vllm, blis-sglang | 3 | each particular is in the engine's surface list or generator at its modelled commit |
| 5 | Lowering out of the graph deriver; `contracts/rules/` removed (DC2, Table DC) | blis-substrate, blis-vllm, blis-sglang | 2 | the deriver writes checkpoint facts only and `contracts/rules/` is gone |
| 6 | Engine-path coefficients keyed by the identity of the code that does the work: `CodeID`, `code_paths.json`, `host_cpu` (§3.2, Table DC) | blis-substrate | none | a coefficient lookup fails on a different `CodeID` |
| 7 | Kernel lists, the cross-generation transfer rule and the ledger's client multiples (Table DC, Substrate and simulator). The transfer rule is validated before any GB200 transfer is used | blis-substrate, inference-sim | 2 | the freshness check passes and the transfer rule is validated, or transfers rank as roofline |
| 8 | Simplifications of design v2.1.0, v2.2.0 and v2.4.0: the `ledger`, `invariants` and `compose` commands removed, the ledger no longer embedded, the gated-config nightly deleted with its environment and secret, the InferenceX regeneration step dropped from the ledger nightly, the maintainer steps in the READMEs and PR template, the stale dashboard comment, the report role removed (Table DC) | inference-sim, blis-substrate, accuracy-dashboard | none | each deletion has merged and CI passes without it |
| 9 | Mistral-Large-4 and Inkling-2-Small on GB200: catalog entries, model support, coefficients (DC4). Starts when the maintainer records the engine upgrade (DC4, Open) | blis-vllm, blis-substrate | 3, 6, 7 | each scenario simulates on GB200 with every coefficient's method named, and the team's verification run is recorded |
| 10 | Ingestion: the ledger follows each source, and the dump is reconciled with the API (§3A.1, §3A.9) | blis-substrate | none | a scheduled job ingests API rows together with the dump, and the straddling-run test passes |
| 11 | Archive of the sources that expire (start now; §3A.3) | blis-substrate | none | an expiring log can be read from the private archive after the source deletes it |
| 12 | Count of anchor units whose inputs can be recovered, without simulating (§3A.8) | accuracy-dashboard | none | the count is published |
| 13 | The new calibration sources ingested, with training-only roles (§1, §1.4) | blis-substrate | 10, 11 | each source's units are in the ledger with training roles only |
| 14 | Settings provenance: each source's scenario writer has a field-against-record test, and the confirmations of §2.4 are made (§2.2, §2.4) | blis-substrate | 13 | every field is tested against its record and the three confirmations are recorded |
| 15 | Engine and table coverage: SGLang field list, router table, the settings no engine module models (§3A.4) | blis-sglang, blis-vllm, inference-sim, blis-substrate | 6 | each listed blocker is modelled, proven inert, given an estimation rule or refused by name |
| 16 | Scoring: no age limit, commit distances, funnels for InferenceX and configiq (§3A.2, §3A.5, §3A.6) | accuracy-dashboard | 3, 10, 12 | the funnels publish, and an old anchor unit with recoverable inputs is scored |
| 17 | configiq as a ledger source: the rule for each writer, and a pinned revision (§3C). The pin can be done first | blis-substrate, accuracy-dashboard | 10 | each writer's family has a rule and the revision is pinned |
| 18 | Calibration acceptance gates fixed in advance, with the maintainer's thresholds (§1.5, Open), and roles drawn per role key (§1.4). Merged before any fit | blis-substrate | 6, 13, 14 | the gates and thresholds are merged before any fit reads the new sources |
| 19 | Dashboard: slicing by any attribute, and the rule for small slices (§3B) | accuracy-dashboard | 16 | COV-13's tests pass: ten points from two role keys render no aggregate |
| 20 | blis-config-search#110, first workstream: nested native speculative settings with recursive provenance (§0.5) | blis-config-search | 15 | provenance round-trips |
| 21 | blis-config-search#110, other three workstreams: bounded sharding, per-attempt journal, server-series diagnostics (§0.5) | blis-config-search | none | each workstream's test of §0.5 passes |
| 22 | CI checks product correctness only: an `edited` event triggers nothing, the process checks are retired, and stale citations are updated (§4, Table DC "Process checks" and "Stale citations"); inference-sim's workflows once row 2 lands | each repository's workflows; the substrate's shared checks | none | an `edited` event triggers nothing; no check reads pull-request text or an issue; the scheduled `blis` workflow is gone and main is green in every repository |
| 23 | The items moved to M3.2 by decision: GB200 decode cost (blis-vllm#272, blis-substrate#140), KV pool size (blis-vllm#158), blis-substrate#369, blis-sglang#141, and the smaller items of §0.2 and §0.6 | as listed | none | each item is merged or closed with a record |
| 24 | The 150 open M3.1 issues (§0.4), each taken into the row its plan item matches; the issue numbers are re-mapped after the transfer | as listed in `m31-carried.tsv` | 2 | each issue is closed or named in a row above |

Row 18's gates must be written and merged before any fitting reads the new sources (VAL-6: the split and success
criteria are committed first).
