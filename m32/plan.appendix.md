## Plan decisions — now in the requirements

The decisions drafted here have been folded into the requirements above, where they are authoritative:
the small-slice guard (§3B), the configuration-level partition rule (§1.4), the calibration acceptance
gates (§1.5), and the `blis-config-search#110` disposition (§0.4). This section is kept only as an index
to them, so the plan carries no decision that the requirements do not.

## Prerequisites — start now

- **Harvest the expiring sources immediately.** The SGLang nightly job logs and `consolidated-metrics`,
  and Tritonbench, expire at ~90 days. Begin the pinned private archive now, so the window keeps growing
  instead of rolling off before M3.2 starts.
- **"No new GPU or cluster runs" has one exception.** The real-vLLM load-timing test (blis-vllm#305)
  uses already-posted real data, so it is not a new run; the GB200 custom all-reduce (blis-substrate#116)
  is a genuinely new micro-measurement on GB200 and is the one exception — to be tracked under
  blis-substrate#116 or a new issue (none is filed for the measurement yet).

## Execution — ownership and sequence

Still requirements, not yet an executable plan. The carried M3.1 issues are dispositioned
([`m31-carried.tsv`](m31-carried.tsv)), but the M3.2 work needs an ordered PR sequence. Workstreams in
dependency order (PR numbers to be assigned at the cut):

| # | Workstream | Owner repo(s) | Depends on |
|---|---|---|---|
| 1 | Engine-path coefficient contract — host/scheduler/launch/replay keyed by code identity (§3) | blis-design, blis-substrate | — **(no issue/PR yet; gates every per-engine cost)** |
| 2 | Ingestion: ledger-follows-source auto-pin + dump/API reconciliation (§3A.1, §3A.9) | blis-substrate | — |
| 3 | Archival of the expiring sources (start immediately) | blis-substrate | — (not blocked on ingestion) |
| 4 | New calibration sources ingested, fit-only roles (§1, §1.4) | blis-substrate | 2, 3 |
| 5 | Input-recoverability census, no simulation (§3A.8) | accuracy-dashboard | — (pre-plan; does not wait on ingestion) |
| 6 | Engine/table coverage: SGLang field list, router table, vLLM settings tail (§3A.4) | blis-sglang, blis-vllm, inference-sim, blis-substrate | 1 |
| 7 | Scoring: no age gate, release-distance grades, funnel per source (§3A.2/§3A.5/§3A.6) | accuracy-dashboard | 2, 5 |
| 8 | configiq as a ledger source, family rule, pinned revision (§3C) | blis-substrate, accuracy-dashboard | 2 |
| 9 | Calibration acceptance gates + partition rule precommitted | blis-substrate | 1, 4 — before any fit |
| 10 | Dashboard UI: slicing, small-slice guard, min_points legibility | accuracy-dashboard | 7 |
| 11 | blis-config-search#110 successors — the four workstreams (§0.4) | blis-config-search | only (i) on 6; (ii)/(iii)/(iv) independent |
| 12 | CI: a PR text edit must not change merge state (§5) | blis-design + each repo's ci.yml | — |

Workstream 9's gates must be written and merged **before** any fitting reads the new sources (X8).
Workstream 1 has no design issue or PR yet and blocks every per-engine cost; file it first.
