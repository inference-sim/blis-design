## Plan decisions (resolving open items above)

Plan-authored; these resolve items the requirements leave open, and carry no source numbers of their
own (so nothing here can drift from `requirements.md`). They should be folded back into the
requirements as they are accepted.

- **Small-slice guard** (resolves §3B's open wording). Raw point rows are always visible at every *n*;
  an aggregate accuracy figure is always withheld below `min_points` (10) **at every level** — headline
  and every drilled-in leaf alike — and a withheld aggregate is excluded from every verdict. The
  threshold stays; a test pins it. UI legibility (show `n=3 · mean held`, not a bare verdict; the points
  table states the rule) is tracked in accuracy-dashboard#160.
- **`blis-config-search#110` disposition.** The old #110 draft is **superseded**; the M2/M3.1 overlap
  (`draft_model`, acceptance recording, CPU/per-pool offload — already supplied) is removed from scope.
  The remainder is four successor workstreams, all owned by `blis-config-search`, each with a done-when
  test and a PR number to be assigned: (i) nested native speculative settings + recursive provenance
  (round-trip provenance); (ii) bounded exact-search sharding (exact sharded/unsharded multiset
  equality); (iii) durable per-attempt journal, passed/refused/incomplete retained (interruption /
  no-truncation); (iv) optional server-series diagnostics (collection that does not change scoring).
- **Calibration acceptance gates** (precommit, X8). Before any fit reads the new sources, precommit: the
  baseline each fit must beat; the error metric and its mandatory slices (engine, chip, workload at
  least); the minimum sample count per slice for a verdict (at least `min_points`); the allowable
  per-engine / per-chip regression elsewhere; the held/anchor verdict, evaluated once after selection;
  and the revise-or-revert rule.
- **Partition rule** (replacing the loose "a source never both fits and grades"). InferenceX and
  configiq deliberately provide both training and held partitions. The split is assigned at the
  **role-key (configuration) level** — source, model, hardware, precision, framework, benchmark type,
  configuration hash — not per row, so every concurrency and repetition of one configuration shares a
  role and correlated repetitions never straddle the fit↔held boundary. A coefficient is never selected
  or graded on the role-group that fit it. New sources draw fit/select/validate only.

## Prerequisites — start now

- **Harvest the expiring sources immediately.** The SGLang nightly job logs and `consolidated-metrics`,
  and Tritonbench, expire at ~90 days. Begin the pinned private archive now, so the window keeps growing
  instead of rolling off before M3.2 starts.
- **"No new GPU or cluster runs" has one exception.** The real-vLLM load-timing test (blis-vllm#305)
  uses already-posted real data, so it is not a new run; the GB200 custom all-reduce (blis-substrate#116)
  is a genuinely new micro-measurement on GB200 and is the one exception, filed as its own issue.

## Execution — ownership and sequence

Still requirements, not yet an executable plan. The carried M3.1 issues are dispositioned
([`m31-carried.tsv`](m31-carried.tsv)), but the M3.2 work needs an ordered PR sequence. Workstreams in
dependency order (PR numbers to be assigned at the cut):

| # | Workstream | Owner repo(s) | Depends on |
|---|---|---|---|
| 1 | Engine-path coefficient contract — host/scheduler/launch/replay keyed by code identity (§3) | blis-design, blis-substrate | — **(no issue/PR yet; gates every per-engine cost)** |
| 2 | Ingestion: ledger-follows-source auto-pin + dump/API reconciliation (§3A.1, §3A.9) | blis-substrate | — |
| 3 | Archival of the expiring sources | blis-substrate | 2 |
| 4 | New calibration sources ingested, fit-only roles (§1, §1.4) | blis-substrate | 2, 3 |
| 5 | Input-recoverability census, no simulation (§3A.8) | accuracy-dashboard | 2 |
| 6 | Engine/table coverage: SGLang field list, router table, settings tail (§3A.4) | blis-sglang, blis-substrate | 1 |
| 7 | Scoring: no age gate, release-distance grades, funnel per source (§3A.2/§3A.5/§3A.6) | accuracy-dashboard | 2, 5 |
| 8 | configiq as a ledger source, family rule, pinned revision (§3C) | blis-substrate, accuracy-dashboard | 2 |
| 9 | Calibration acceptance gates + partition rule precommitted | blis-substrate | 1, 4 — before any fit |
| 10 | Dashboard UI: slicing, small-slice guard, min_points legibility | accuracy-dashboard | 7 |
| 11 | config-search #110 successors — the four workstreams | blis-config-search | 6 |

Workstream 9's gates must be written and merged **before** any fitting reads the new sources (X8).
Workstream 1 has no design issue or PR yet and blocks every per-engine cost; file it first.
