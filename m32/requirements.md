# BLIS M3.2 requirements (working capture, started 2026-11-18)

Status: being captured with the maintainer; more requirements to come. Not yet a design or plan.
**2026-11-18: the maintainer accepted the proposals in sections 1, 2 and 3** (1.2, 2.2-2.4, 3.2). 1.3 stays open.
Each item says whose it is: **maintainer** (stated by them) or **proposal** (open to correction).
Supporting evidence is in `evidence/` next to this file: what each project publishes (`INVENTORY.md`), where each
new source records its settings (`SETTINGS-PROVENANCE.md`), why so few points are scored (`COVERAGE-FUNNEL.md`),
and how configiq rows are produced (`CONFIGIQ-FINDINGS.md`).

## 0. Carried from M3.1

**Maintainer.** Whatever was planned for M3.1 and does not make the M3.1 cut is handled in M3.2. Nothing planned
for M3.1 is dropped silently: an issue is either closed by the M3.1 pull requests or listed here.

M3.1's plan is the release plan's §3.1 (`plan/m31_scope.tsv`, 189 issues). The M3.1 set is seven pull requests,
all still open: blis-substrate#361, blis-vllm#275, blis-sglang#126, llm-d-router#21, inference-sim#2237,
accuracy-dashboard#133 and blis-config-search#150. Status below is as of 2026-11-18 16:55 UTC; it is refreshed
from the final pull-request bodies at the cut.

**0.1 Review findings still being fixed for M3.1.** These land in M3.1. Any that miss the cut move to M3.2.
- *Finish after Schedule in SGLang* (blocking for one reviewer on blis-sglang#126, and for both on
  inference-sim#2237). The engine fix is merged (blis-sglang#150, head `03d72d6f`). inference-sim still pins the
  engine head from before the fix (`a721ab16`). Still to do, and not yet in a pull request: re-pin it, and add an
  integration test that puts an SGLang deadline between Schedule and Complete.
- *Per-pool KV connector and offload* (blis-substrate#307, required for M3.1 by review). blis-substrate#402 is
  merged; blis-vllm#302 and inference-sim#2252 are open. CPU-offload sweeps on P/D in config-search
  (blis-config-search#94) follow once #307 lands; that change is not yet in a pull request.
- *Borrowed acceptance named on stderr* (inference-sim#2079): inference-sim#2250 is open.
- *config-search review fixes*: the acceptance entry (part of #93), probe packaging and the demo re-run are in
  blis-config-search#155, which is open.
- *A simulator refusal is a named not-scored point*: accuracy-dashboard#158 and blis-design#32 are open.

Already fixed in review, merged into the integration branches:
- the measured Muse DSpark acceptance in the 21 scenarios (inference-sim#2248);
- the DeepSeek 1P1D scenario's flags (inference-sim#2248);
- pool chips refused without a node-pool bundle, #2221 (inference-sim#2249);
- P/D per-instance measured window, #2218 (inference-sim#2246);
- p2p at unequal TP, #2214 and #2220 (inference-sim#2251);
- the router check, #2219 (inference-sim#2247);
- the all-reduce lane keyed by backend, blis-substrate#116 (blis-substrate#373);
- the body corrections.

**0.2 Moved to M3.2 by decision.**
- blis-sglang#141, SGLang's SchedulerRecvSkipper (draft, checks red).
- GB200 decode cost: blis-vllm#272 (Muse Spark's fused-kernel launches, held) and blis-substrate#140 (the 3.2 µs
  launch cost still used on GB200). Until both land, GB200 decode stays about 1.35 times slow per token.
- blis-substrate#125: no engine pads a drafter's DP batch yet.
- blis-vllm#158: Muse Spark's KV pool is still 1.25 to 1.30 times the engine's at TP8, and 1.88 to 2.04 times with
  DSpark, against a 5% target.
- blis-substrate#369: the pre-registration and held-out verdict for the Blackwell launch fit.
- Smaller items: the `moe_backend` and `mm_encoder_tp` settings, rows whose record returns 404, the mooncake-atom
  rows, the DeepSeek-V4 environment-variable bundle, and the "same kernels" wording of blis-substrate#294 and
  blis-vllm#298.
- On the dashboard: the chip-split card, and SGLang rows on the public cards.
- Scored lanes for the internal studies: none is scored yet (accuracy-dashboard#133 review). This is covered by §3A.

**0.3 M3.1 plan issues the M3.1 set does not close.** Of the 189:
- 21 are already closed, and 26 close when the set merges;
- 32 are advanced but stay open;
- 108 are not yet named by any of the seven bodies.

Some of the 108 were advanced by item pull requests merged into the integration branches without a closing
line. Each is checked against the final bodies at the cut, and is closed there if it is done. The rest carry
into M3.2.

| Item | Advanced, not closed | Not closed or named |
|---|---|---|
| P1 Release by commit | substrate #193, #343, #345 | sim #2145, #2149; substrate #204, #340 |
| P2 M3.0 review debt | substrate #335, #337 | substrate #331, #332, #338 |
| H1 Pull requests held from M3.0 | – | sim #1493, #1495, #2052, #2129 |
| B1 Correctness | substrate #310; vllm #214 | config-search #129, #133; dashboard #100; sglang #55, #91; sim #2152 |
| A1 Launch and step cost per chip | substrate #242; vllm #161, #191 | substrate #93, #114, #115, #121, #134, #136, #140, #152; vllm #72 |
| C1 Dashboard coverage | – | dashboard #22, #58, #62, #63, #65, #79, #83, #87, #89, #90, #110, #111 |
| C2 SGLang end to end | – | sglang #32, #40, #44, #56, #57, #62, #63, #64, #65, #66, #67, #68, #70, #71, #73, #74, #75, #76 |
| S1 Every capability sweepable | config-search #93, #125, #138 | – |
| R1 Command-line surface | – | sim #2216 |
| A2 Time before the engine, and prefill | – | sim #2094; substrate #75, #94 |
| A3 KV capacity and memory | sim #1969; substrate #255, #281; vllm #73, #129, #158 | substrate #73, #76, #132, #294 |
| C3 Closeness grades | – | dashboard #53; sim #2101, #2103; substrate #41, #43 |
| C5 Catalog by points blocked | substrate #317 | dashboard #7; substrate #91, #105, #106, #109, #126, #179, #188, #245, #258 |
| A4 Collectives and MoE paths | substrate #150; vllm #75 | substrate #118, #123, #137, #146; vllm #74, #108 |
| A5 Speculative acceptance | substrate #125, #164 | dashboard #59, #80; sim #2115, #2125, #2136, #2141, #2142; substrate #144 |
| T1 Data-parallel serving and network structure | sim #2126; substrate #48, #49, #346; vllm #64 | dashboard #61, #64, #91; sim #1988, #2146, #2164; substrate #50, #51, #153, #161 |
| T2 KV tiers under P/D | vllm #47, #132, #146 | sim #2202, #2203; vllm #184, #190, #204 |

In C2, SGLang speculation, attention-DP, EP and P/D (sglang #64 to #71) stay refused in M3.1, as blis-sglang#126
states. A blis-substrate#51 comment says what remains after switch groups. Repositories are `inference-sim/<repo>`.

The per-issue outcome for all 106 is committed in [`m31-carried.tsv`](m31-carried.tsv) (columns: issue, item,
group, M3.1 PRs, note). Groups 1–2 are body edits; groups 3–4 carry into M3.2.

## 1. New data sources for calibration

1.1 **Maintainer.** Bring these data sources into BLIS properly for calibration:
- SGLang nightly profiler traces, `github.com/sgl-project/ci-data` (step and host overhead, kernels);
- the vLLM CI perf API, `ci.vllm.ai/api/perf`, with the `vllm-project/perf-eval` recipes (current vLLM on H200 and B200);
- SGLang nightly job logs and `consolidated-metrics` artifacts (scheduler behaviour, resolved server arguments).

1.2 **Maintainer.** Licence is not a blocker: the data is queried, not redistributed.
**Proposal.** So none of it is committed to a public repo (D6). Units are built from a pinned fetch at fit
time, the way the private internal data is handled, and a public figure cites the source URL and fetch date.

1.3 **Open.** Whether the rest of the inventory (Tritonbench nightly, SGLang AMD P/D nightly, llm-d Prism
archive, blog step tables, MoE tuning configs, AgentX launch configs) is also in M3.2 scope.

1.4 **Maintainer (2026-11-18).** The new data sets are used entirely for fitting and calibration. Accuracy
reporting on accuracy-dashboard covers only the InferenceX and configiq points held out for it. Everything
else is available to M3.2 for training, fitting and validation, used however serves accuracy best.
**Proposal**, to apply this:
- *Roles for new sources.* Each new source's ledger rule draws only fit, select and validate roles, with no held
  or anchor share. The split among those three is M3.2's choice per source.
- *What stays held out.* InferenceX and configiq keep their held and anchor shares, untouched. Accuracy figures
  come only from those.
- *Everything else* is training or validation data: InferenceX's and configiq's fit, select and validate shares,
  AISimulate's sweeps and forward-pass set, the internal experiments, and any source added under 1.3.
- *No double use.* A source that fits a coefficient never also grades it. Selection between candidate fits uses
  the select and validate shares, never the held-out points.

## 2. Settings identification (apples to apples)

2.1 **Maintainer.** For every point used, it must be easy to find out the run's settings: workload,
cluster, GPU type, model and engine settings. Getting these right is what makes the comparison like for
like. Identifying the settings correctly is part of the M3.2 calibration process, not a one-off.

2.2 **Proposal.** Follow the standing rule: every value comes from the run's own records; a value no
record holds is a named substitution with its source and lowers the grade; never a BLIS default. Each
source's scenario writer has a test that checks every field against the record it came from.

2.3 **Proposal.** Per source, the record that settles each setting (from SETTINGS-PROVENANCE.md):

| Setting | vLLM CI perf API | SGLang nightly metrics + logs | SGLang traces |
|---|---|---|---|
| Engine commit | row `image` tag (some rows unpinned) | run `head_sha` / `commit_sha` | trace run id -> Actions run `head_sha` |
| GPU, count | row `device`; recipe `gpu`, `num_gpus` | runner label (`8-gpu-h200`) | trace `deviceProperties`; runner label |
| Model, precision | row `model`, `precision`; recipe | metrics `model`; log | trace directory name; test definition at commit |
| Parallelism | recipe `serve_args` (row `tp` is TP x DP) | log `server_args` dump | test definition at commit; `distributedInfo` |
| Engine settings | recipe `serve_args` + vLLM defaults at commit (server log private) | log `server_args` (resolved) | test definition at commit (logs expired) |
| Workload | recipe `vllm_bench` block + `run_vllm_bench.sh` | `one_batch_server.py` args at commit (static batch, seed 42) | `bs`, `il` in file name + profiler step settings |
| Metric definition | `vllm bench serve` means/medians/p99, seconds, aggregated over 3 repetitions | `latency`, `last_ttft` (last request, not mean) | per-step spans, rank 0 only |
| Host / cluster | `lib/gpu_profiles.yaml` (env, docker vs k8s) | runner definition | runner definition |

2.4 **Proposal.** Values to confirm before any fit: the statistic `aggregate_perf.py` uses over
repetitions; `vllm bench` seed and range ratio at each commit; how the recipe's revision is matched to a
row's date when the recipe changed that day.

## 3. Which engine the data improves

3.1 **Maintainer.** Use calibration to improve both SGLang and vLLM as much as possible. Data that can only
improve one engine (because of the fit-the-engine-you-predict match) is still used, not ignored. Some
coefficients are shared and others are not, and that is fine.

3.2 **Proposal.** Kernel coefficients stay keyed by kernel implementation, so SGLang data fits vLLM's
value wherever both run the same implementation. Engine-path costs (host, scheduler, launch, CUDA-graph
replay) get keyed by the identity of the code that does the work, so each engine has its own value
without an engine name in substrate (X2). Today host overheads are scoped by hardware and model only; this
is a design change that lands before the plan.

## 3A. Maximise scorable coverage

**Maintainer.** Don't leave scorable points on the table: maximise coverage, especially for InferenceX. Today
199 of 20,364 InferenceX anchors are scored (nightly 2026-11-17, v0.17.1), and about 213 of 1,702 configiq
units can be simulated. The funnel and its evidence are in `evidence/COVERAGE-FUNNEL.md`:
the losses are mostly policy and a frozen ledger, not missing data.

**Proposal (accepted by the maintainer as my recommendation, 2026-11-18).** Older points count in the headline
at their own grade; they are not split off. The grade already says how close a point's setup is to what BLIS
ran, and a separate table would hide coverage. The headline always shows its grade breakdown, so the
same-release figure is one slice away (3B).

The rest of this section is proposal unless marked.

3A.1 **The ledger follows each source.** Every row InferenceX publishes becomes a ledger unit, not only the
db-dump/2026-09-28 rows plus hand-pinned supplements. New rows are pinned by record id and content SHA-256, as
supplements are today, but generated by the ingest tool on a schedule rather than added by hand. New units
draw their roles by the existing rule, so no partition change is needed. Today 1,287 in-scope rows published
after the dump are not units at all (794 single-node vLLM/SGLang). Every new source in §1 also joins the ledger
continuously, with training roles only (1.4).

3A.2 **No age limit on scoring.** The 180-day window stops being a gate: every anchor whose inputs can be
recovered is scored, at its grade. It removes 12,491 in-scope anchors today, as their only reason. A date range
becomes a slice (3B).

3A.3 **Recover inputs from durable records, and keep the ones that expire.**
- vLLM single-turn: the API's `/server-log` (verified 200 for rows from 2026-02 and 2026-03).
- SGLang and P/D: the job log while GitHub holds it, else the recipe or script at the run's commit (the pull
  already does this).
- Measurements the API has superseded: the dump.
- Inputs that expire (GitHub job logs and artifacts, about 90 days; agentic exports): archived privately as they
  are pulled, never committed publicly (D6), so a point stays re-scorable after the source deletes them.
A point whose inputs are truly gone is G5 with a reason that says which record is gone.

3A.4 **Engine and table gaps, ranked by points held back.**
- SGLang: scored from M3.1's blis-sglang field list (186 in-window anchors blocked today, 109 by that alone; about
  5,000 SGLang and Dynamo-SGLang anchors in all).
- The router table maps Dynamo's router (252 in-window anchors).
- The not-modelled settings tail (`data_parallel_rpc_port`, NCCL and FlashInfer environment variables,
  `use_trtllm_attention`, `moe_backend`, ...): each is modelled, proven inert, or given an estimation rule, in
  order of the points it alone holds back.
- TRT-LLM stays refused: BLIS has no TRT engine.

3A.5 **Older engine releases are scored, not refused.** A run on a release other than the one an engine repo
models is a named release difference at a lower grade (the existing rule), for both engines.

3A.6 **Coverage is reported as a funnel for each source**, every release: held by the source, units, in scope,
inputs recoverable, scored, by grade, with the top blockers by points they alone hold back. A drop at any stage
is a visible number, not an absence.

3A.7 **configiq.** Waiting on the configiq team's answers (the maintainer asked them). Meanwhile their repos
are being read to recover each setting (§3C).

3A.8 **Expected effect** (maintainer's expectation, 2026-11-18; the shares stay the same, the counts rise).
The role proportions do not change: for new units, 30 fit, 10 select, 10 validate, 30 held and 20 anchor, and
legacy units keep their sides. The held-out points grow because the same proportions now apply to far more
scorable points. Upper bounds from the 2026-11-17 nightly and the ledger:

| | Today | M3.2 ceiling | What opens it |
|---|---|---|---|
| InferenceX anchors scored | 199 | about 2,700, up to about 4,600 | the ~490 unscored in-window anchors; out-of-window anchors measured from 2026-02 on (1,143 vLLM-family, 850 SGLang-family); about 260 anchors among the 1,287 rows published after the dump; up to 1,913 more SGLang-family anchors from before 2026-02 if their recipes at the run's commit still resolve. TRT's 4,827 stay refused. |
| InferenceX held units | not counted on the dashboard | about 1.5 times the anchors | the same levers; held is 30% against anchor's 20% for new units |
| configiq held-out units | not yet published (below) | about 850 of 1,702 (50%) by proportion; about 185 of the 373 forge-written H200/B200 units | §3C's family rule |

These are ceilings, not forecasts. The real count depends mostly on how many old runs' inputs can still be
recovered. The API serves only the latest measurement per configuration, and in M3.1, 213 of 573 matched vLLM
points had their record gone (404).

**Measured 2026-11-18:** the API's `/server-log` was queried for 33 vLLM single-turn records that only the dump
holds, three per month. Every record from 2025-09 to 2026-01 returned 404, and every record from 2026-02 to
2026-07 returned 200. So the 3,758 vLLM-family anchors measured before 2026-02 cannot be rebuilt from their
logs. They stay G5 with that reason unless another record of their settings is found. SGLang points take their
launch command from the recipe at the run's commit, not from this endpoint, so the older SGLang anchors are
counted as "up to" until that path is checked. It also depends on the Dynamo router mapping and the not-modelled settings
tail. **Proposal:** measure it first, with a pull of every anchor that only checks whether its inputs can be
fetched (no simulation), and report the count before planning.
configiq's units are not yet in the published anchor and fit lists on `main`, so its held-out set must be
published before it can be scored.

3A.9 **Proposal. Reconcile the frozen dump against the live API explicitly.** InferenceX stopped publishing
dumps after `db-dump/2026-09-28` (weekly Apr–Sep 2026, none since), so the pinned dump is a dead, aging
source: its runs sit on ever older vLLM and SGLang releases, while every fresh run comes only from the API.
The id-floor rule (the dump owns record ids up to the cutoff, supplements own the ids above it) is a static
watermark that does not state this. To apply:
- *Call the dump a frozen genesis archive, not a base to advance.* It is the only copy of pre-2026-09-28
  history, including measurements the API has superseded and no longer serves, and it will not grow; all
  forward coverage is 3A.1's auto-pinned API supplements.
- *Keep one `measured_date` per run across the cutoff, as 3A.1's automation runs.* A benchmark run's date is
  the earliest over all its records. Ingest already reads the dump and the API supplements together, so a run
  with early records in the dump and later ones on the API keeps one date and one unit
  (blis-substrate `ledger/cmd/ledger/main.go`, which appends supplement rows before `inferencex.Ingest`; the
  dashboard pull takes the date from the ledger). The constraint is on the automation: it must never ingest
  new API rows apart from the dump. A test should pin it, with a run whose records straddle the cutoff and
  one unit and date on both sides.
- *Grade and route by release distance.* Old-release dump runs carry the 3A.5 grade. Under 1.4's draw, their
  fit, select and validate shares feed calibration. Their held and anchor shares count in the headline at that
  lower grade (3A, the maintainer's decision), and the same-release figure is the release-distance slice (3B).
- *Make the split visible.* Keep each point's source (`dump` / `api`) and release distance, and have the
  3A.6 funnel and 3B slices report what share of the held-out set is the frozen dump versus the live API,
  so a headline dominated by old dump runs is a visible number.
- *Never re-pull a dump row from the API.* The two print the same row's numbers differently and the API
  lacks the dump's superseded history; keep the id-floor.

## 3B. Slice accuracy by any recorded attribute

**Maintainer.** As more sources come in, accuracy must be sliceable by all their data attributes. There is a
version of this today.

Today: the summary breaks counts down by engine, engine release, chip and grade, and the UI filters only on
multi-node and estimate tier over a fixed model / hardware / framework grouping.

**Proposal.** Every scored point carries its attributes, and the dashboard filters and groups by any of them,
with every aggregate recomputed from the points that survive (as `filter.ts` already does):
- source and role;
- model, precision, chip, node count, interconnect;
- engine, engine release, release distance from the modelled release;
- topology (TP, DP, EP, P/D pools), speculative method, offload and KV tiers, router;
- workload type, ISL/OSL, concurrency, arrival process, prefix sharing;
- measured date;
- grade and each substitution named on the point.
Each slice shows its point count and coverage beside its accuracy, so a small slice can't pass for a strong
result.

**Proposal.** Make the small-slice guard legible. A figure over fewer than `min_points` points is shown as the
bare text "too few points" at every level of the summary, while the per-point table below it still lists every
measurement, so the two read as a contradiction and the text covers most fine slices. Show the held figure as
its count instead (`n=3 · mean held`), have the per-point table state that no mean is reported below
`min_points`, and stop applying the guard to a leaf the reader has drilled into. The threshold itself stays.
Tracked in accuracy-dashboard#160.

## 3C. configiq: settings and closeness

Evidence: `evidence/CONFIGIQ-FINDINGS.md` (Red Hat repos read 2026-11-18; parser regex and
forge `cpt.yaml` re-verified). The configiq team's answers are still pending; they override anything inferred here.

**Correction.** A blank engine column is "flag not passed" only for rows forge wrote. The publisher regex-parses a
free-text `runtime_args`, and misses space-separated values and bare booleans, so a blank in a manually imported
or Model Furnace row can hide a value the run set. `prefix_caching` blank never means "on".

All proposal, pending the team's answers:

3C.1 **Classify each row by writer.** Family A is forge, recognised by a `/v1/...` request type and prefix caching
on: 779 units, 373 on H200 or B200. Family C is manual imports, 128 units. Family D is Model Furnace and older
manual imports, 803 units. The family decides how blanks are read.

3C.2 **Family A: fill every blank from forge's own records**, named as the substitutions they are:
- the CPT matrix (`cpt.d/cpt.yaml`) and the presets at the commit in force on the run's date, matched on model, TP,
  KV dtype and request type;
- vLLM's defaults at that release and device, for flags forge never passes (`max_num_seqs`, chunked prefill,
  `max_num_batched_tokens`, precision);
- the frame from forge's history: concurrent profile, 275 s window from 2026-09-22, the warm-up and ramp-up then in
  force, GuideLLM release, seed 42, `ignore_eos`, streaming.
This replaces today's preset match, which misses `cpt.yaml`.

3C.3 **Family D: fill only what the public guide and furnace defaults support**: prefix caching off and a 450 s
or 600 s window when `max_seq_len` is 8192 or 10000 and memory utilisation is 0.92. These are named estimated
substitutions at a lower grade. Rows whose TP is 1 may have used data parallelism and stay unscored.

3C.4 **Check each filled frame against the data.** The window derived by Little's law from the concurrency-1
row must agree with the frame used. Only successful requests are compared.

3C.5 **Model each configiq workload as it ran**: the multi-turn shapes (`benchconf` `interactive-chat`, about a
4,000-token first prompt, 45 s between turns) and the prefix workloads.

3C.6 **Pin the dataset revision.** It is not append-only: 444 rows were removed between revisions.

3C.7 **Ask Red Hat** (the maintainer owns this conversation):
- publish an allow-listed `runtime_args`, the image tag, the GuideLLM version, the cluster tag, the start and end
  times, DP and the turn index;
- fix the case mismatch that drops DP;
- publish more of the roughly 52 models the CSV holds.

## 4. Proposals not yet discussed

4.1 Start harvesting the 90-day sources now (SGLang job logs and metrics artifacts; Tritonbench), before
M3.2 starts, so the window keeps growing instead of rolling off.
4.2 Points on engine releases other than the one each engine repo models are scored as a named release
difference (vLLM rows across many nightlies; SGLang traces from before v0.5.23).
4.3 *Superseded by 1.4:* new sources are not reported on accuracy-dashboard. The dashboard may still show how
well the fitted model reproduces them, as a training diagnostic labelled as such, never as accuracy.
