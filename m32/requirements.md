# BLIS M3.2 requirements (working capture, started 2026-11-18)

Status: being captured with the maintainer; more requirements to come. Not yet a design or plan.
**2026-11-18: the maintainer accepted the proposals in sections 1, 2 and 3** (1.2, 2.2-2.4, 3.2). 1.3 stays open.
**Section D (design changes) is a proposal under team review**; nothing in it is decided.
Each item says whose it is: **maintainer** (stated by them) or **proposal** (open to correction).
Supporting evidence is in `evidence/` next to this file: what each project publishes (`INVENTORY.md`), where each
new source records its settings (`SETTINGS-PROVENANCE.md`), why so few points are scored (`COVERAGE-FUNNEL.md`),
and how configiq rows are produced (`CONFIGIQ-FINDINGS.md`).

## D. Design changes M3.2 needs (proposal, for team review)

**Status.** Proposal, raised by the maintainer on 2026-11-18 for the team to review. Nothing in this section is
decided or built until the review closes. Each change to the standing design lands first as a blis-design pull
request to `main`, then in code. Whether D4 belongs in M3.2 or in a patch release of M3.1 is open.

**Why.** Three things recur.
- *Cross-repository friction.* Most features touch contracts, an engine and the simulator together, and each
  repository boundary turns one change into a sequence. A change to blis-substrate is re-pinned in blis-vllm,
  blis-sglang and the router fork, then in inference-sim, with full CI at every hop. In M3.1, blis-substrate#373
  was first held out because that cascade "cannot be green in the window". The per-pool offload fix took three
  sequential pull requests: blis-substrate#402, blis-vllm#302 and inference-sim#2252.
- *Teams ask for models that only an unreleased engine build supports* (D4).
- *The new data is pinned to engine commits, not releases.* Every vLLM CI perf row names a vLLM commit, and every
  SGLang nightly names an SGLang commit (§1, §2.3). Today BLIS can model only a release, so those runs are all
  release differences.

### D1. Model any upstream commit, not only a release (vLLM and SGLang)

**Today.** An engine module models one upstream release (LIF-5). A build runs one release of each engine, and a
scenario that names another is refused (LIF-6). A run on another release is scored as a named release
difference (§3A.5).

**Proposal.**
- An engine module models one upstream **commit**. It may be a release tag or a commit on the upstream's main or
  release branch. The Upstream record names the commit, and the release it descends from. A build still runs
  one commit of each engine, so LIF-6's refusal stays as it is, with a commit in place of a release.
- A move between upstream commits is ported as a diff, as v0.32.0 to v0.33.0 was. The generators (`fields.json`, `surface.json`, `kernel_impls.json`) already take the
  upstream reference as a parameter. The oracle environment is locked per commit.
- **Grading.** A point whose run used the modelled commit is not a release difference. Any other point names its
  distance: commits apart, and releases apart where the two commits sit in different releases.
- **Model backport.** This is the narrow case. The upstream commits that add one model are applied onto the
  modelled commit and listed in the Upstream record. A backport carries model code only, never scheduler, KV or
  connector changes. It folds away when the modelled commit contains it.
- **When to move.** Move the modelled commit on each upstream release, and on demand when a team scenario needs
  a later commit. Each move re-runs the oracle and the goldens.

**Effect.** New models on upstream main can be modelled (D4). The vLLM CI perf and SGLang nightly runs can be
fitted against the exact engine code that produced them (§1). Release-difference grading becomes commit
distance, which is finer.

### D2. Lowering out of blis-substrate, brought forward from M4

**Today.** The catalog's graph deriver still holds vLLM lowering. The plan moved its removal, and the
contract-change review set that removes `contracts/rules/` with model values moved into graph fields, from M3 to
M4 (2026-11-17). The design already says a graph holds only what the checkpoint states, and that sharding,
fusion, padding and the nodes emitted under a layout are lowering (SUB-15). It also says onboarding a model is
one blis-substrate pull request with no engine code (§12.1, T-M1). Neither is true yet.

**Proposal.** Bring both into M3.2.
- Move all lowering into the engine modules.
- Remove `contracts/rules/`, as the contract-change review set (§12.8).

No separate preflight command is needed. §12.1 describes one (`inference-sim onboard --plan`), which was never
built. A run of the requested scenario already answers the same questions: a missing catalog entry or graph
handler is refused by name (`not_in_catalog`), an engine refuses what it cannot lower, and the Result records
which method each coefficient came from, which the dashboard reads as `coefficient_method`.

**Effect.** Onboarding a new architecture becomes a graph handler plus data, and each engine lowers the new
primitives in its own code. A team's model request is answered by running its scenario: what runs, what is
refused and why, and which coefficients come from which method.

### D3. Consolidate blis-substrate, blis-vllm, blis-sglang and blis-kvstore into inference-sim

**Proposal.** Move the four repositories into inference-sim as top-level directories, keeping their history (a
subtree merge) and transferring their open issues.
- `contracts/` becomes its own small Go module inside the repository, versioned, because the router fork imports
  it. SUB-1 already limits it to the standard library and the YAML parser.
- These stay separate:
  - the router fork, a fork of llm-d with upstream's import path;
  - accuracy-dashboard, because a scorer independent of the simulator is a deliberate audit property;
  - blis-config-search, which consumes simulator releases;
  - blis-design.

**Separation of concerns is kept by checks, not by repository walls.**

| Rule | Kept by |
|---|---|
| No engine name or policy in blis-substrate (X2); the cost model imports no engine module; no engine module imports another or blis-kvstore (KVS-2) | an import-graph lint over directories (`go list`), required in CI |
| Each area's heavy CI (oracles, mutation sweeps, byte gate) | path-filtered workflows, so a change runs only the jobs of the directories it touches |
| Review ownership | `CODEOWNERS` per directory; the review agent's questions per area, unchanged |
| One upstream commit of each engine per build (LIF-6) | unchanged; the build's engine directories each name one commit |

**What changes.** One pull request can span the contracts, an engine and the simulator. The bottom-up merge
order and the cascade of pins between BLIS repositories go away (X10, X11). Per-engine release branches (§14.4)
become release branches of inference-sim, which already cuts `release-v0.18`. The rule that blis-substrate is
one Go module (SUB-13) is restated for the new layout.

**What is given up.** The hard wall between repositories. A simulator change could edit catalog data in the same
pull request, so the lints and `CODEOWNERS` must do what the walls did. Each repository's merge rules, checks and
workflows have to be consolidated.

**Timing.** At a release boundary, after the M3.1 cut, as the first M3.2 item, because D1 and D2 are easier in
one repository. The migration is not sized yet. A sizing from the actual workflows, checks and open issues comes
before the decision.

### D4. Support requested by a team: Mistral-Large-4 and Inkling-2-Small on GB200

**Request.** A GB200 configuration for both models on 16 GPUs (Muse Spark's capacity), for the team to use and
verify.

**Facts** (checked 2026-11-18).
- **Mistral-Large-4.** `MistralLarge4ForCausalLM`, with a DSpark drafter. It is in vLLM v0.34.0, released
  2026-11-16, and not in v0.33.0, which blis-vllm models. Its Hugging Face repository is gated.
- **Inkling-2-Small.** `Inkling2ForConditionalGeneration`, 594B. It is only on vLLM main, in vllm-project/vllm#67325,
  merged 2026-11-18 as `abb8194dc3`, and not in v0.34.0. Recent vLLM releases came about two weeks apart.
  blis-substrate#88 tracks it.

**Proposal.**
- Mistral-Large-4 comes with the v0.34.0 port.
- Inkling-2-Small comes with D1, at `abb8194dc3` or later, or with the v0.35 port if that release is near.
- Each model gets its catalog entry and graph handler, and its drafters, under D2.
- Answer each request with its confidence. Neither model has measured runs on GB200, so the configuration is a
  prediction with no held-out evidence. GB200 decode is about 1.35 times slow per token until blis-substrate#140
  and blis-vllm#272 land (§0.2).

### D5. Changes blis-design needs

The standing design and the release plan both change. Each item is one blis-design pull request to `main`,
except where items share lines.

| Design area | Change | For |
|---|---|---|
| §2 Shape, §2.2 ownership table, the repository tree | the four repositories become directories of inference-sim; `contracts/` its own module | D3 |
| §5 repository cards | merge the blis-substrate, blis-vllm, blis-sglang and blis-kvstore cards into inference-sim's, keep a card for the `contracts` module; restate each check's "Runs in" by directory | D3 |
| §6 engine boundary, X2, KVS-2 | the same rules, checked by an import-graph lint over directories | D3 |
| §7.6 port as a unit; §7.1 engine port frame | "at an exact pin" means an upstream commit; the model backport | D1 |
| §8 lowering; SUB-15 | lowering lives only in engine modules; the deriver writes checkpoint facts only | D2 |
| §11.2 to §11.4 grading | release difference becomes commit distance | D1 |
| §12.1 onboarding; T-M1 | one pull request touching the catalog directory; a run of the requested scenario is the preflight, and the `onboard --plan` command is removed from the design | D2, D3 |
| §12.8 contract-change review set | one pull request in one repository, plus the router fork | D3 |
| §13 automation | the release bot without the pin cascade; path-filtered CI | D3 |
| §14 versions: LIF-2, LIF-4, LIF-5, LIF-6, §14.4; X10, X11; SUB-13 | an engine models one commit; one repository's release branches; pins only to `contracts` and the router fork | D1, D3 |
| The invariant registry (`contracts/invariants`) and its generated appendix | each record's "Runs in" and check names follow the new layout | D3 |
| The release plan | move the M4 lowering item into M3.2; add D1 to D4 to the M3.2 section; map the moved issues | D1 to D4 |

### How D relates to the rest of this document

- §1, §2: per-commit data matches per-commit engines (D1).
- §3.2: engine-path coefficients are keyed by the code that does the work. With D1, that code is pinned by
  upstream commit.
- §3A.5 and 4.2: commit distance replaces release distance.
- §0: the carried M3.1 items are unchanged. After D3, the re-pin cascades behind several of them go away.

### Open questions for the review

1. D1: how often to move the modelled commit, and who decides an on-demand move.
2. D1: does a backport need its own grade, or is commit distance enough?
3. D2: is the `contracts/rules/` removal in scope for M3.2 or only the lowering move?
4. D3: consolidate, or keep the repositories and remove the cascade with tooling (a local `go.work`, a bot that
   runs the cascade, and one CI job that tests every repository at the pull request heads)? Tooling keeps the
   walls, but cross-repository changes stay non-atomic.
5. D4: M3.2, or a patch release of M3.1?

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
- 36 are advanced but stay open (named with a `Part of` line; the bodies moved from 32 as items were added);
- 106 are not yet named by any of the seven bodies.

One mutually-exclusive outcome per issue, reconciling to the whole: 21 + 26 + 36 + 106 = 189.

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

The 106 not-yet-named are enumerated with a proposed outcome in [`m31-carried.tsv`](m31-carried.tsv) (columns:
issue, item, group, M3.1 PRs, note); groups 1–2 are body edits, groups 3–4 carry into M3.2. The authoritative
artifact is the full 189-row manifest, one mutually-exclusive outcome per issue, generated from `plan/m31_scope.tsv`
(in the release plan) at the cut; `m31-carried.tsv` is its not-yet-named subset.

**0.4 `blis-config-search#110` disposition.** The old #110 draft is superseded; the M2/M3.1 overlap (`draft_model`,
acceptance recording, CPU/per-pool offload — already supplied) is out of scope. The remainder is four successor
workstreams in `blis-config-search`, each with its own PR (to be assigned) and a done-when test: (i) nested native
speculative settings and recursive provenance (round-trip provenance); (ii) bounded exact-search sharding (exact
sharded/unsharded multiset equality); (iii) a durable per-attempt journal, passed/refused/incomplete retained
(interruption / no-truncation); (iv) optional server-series diagnostics (collection that does not change scoring).
Only (i) depends on the engine's native speculative field list; (ii), (iii) and (iv) are independent.

**0.5 Accuracy items raised in the M3.1 review, carried to M3.2.** None blocks a run.
- *CPU tier ignores model-resident host memory* (inference-sim#1924, already labelled M3.2). DeepSeek-V4.1's engram
  pins about 203 GB of host memory per node, but the CPU KV tier is sized as if all host memory were free, which
  overstates DeepSeek CPU-offload capacity. DeepSeek-V4.1 P/D with CPU offload is one of the internal studies.
- *Muse DEP8 KV-capacity check* (blis-vllm#253). `muse-gb200-nvl-dep8-dspark.yaml` reports
  `kv_capacity_tokens_per_replica` = 500,977 against 8.09M for `tep8`, with TPOT p50 39 ms at c4. It may be correct
  for DP8 ranks of TP1, but check it against the engine's logged KV size. The config-search smoke test on the M3.1
  head also found DEP8 cannot fit a 1M context (72.5 GiB of KV per rank needed, 40.1 GiB available) — possibly
  right, but unconfirmed.
- *CPU-load completion steps* (blis-vllm#305). BLIS reports a load completing at N+3 steps; add a
  load-to-admission-steps test against real vLLM. Data point: Muse-Spark-Open on 16×GB200, DSpark k=7, uncapped
  AgentX — real TTFT p50 at c64 is 19.35 s with no CPU tier and 3.04 s with a 600 GiB tier; BLIS must reproduce
  the tier helping, not hurting.
- *GB200 custom all-reduce still transferred from GB300* (blis-substrate#116). #373 fixed only the lane (the price
  now follows the resolved backend); the value is unchanged — 13.16 µs, `transferred_from: gb300`, against a ~7 µs
  estimate for the custom lane. Measure the GB200 4- and 8-rank custom all-reduce on GB200 itself; keep #116 open
  until then, or file the measurement as its own issue.

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
- *Partition at the configuration level.* InferenceX and configiq provide both training and held partitions; the
  fit/select/validate/held/anchor split is assigned at the role-key (configuration) level — source, model,
  hardware, precision, framework, benchmark type, configuration hash — not per row, so every concurrency and
  repetition of one configuration shares a role and correlated repetitions never straddle the fit↔held boundary.
  A coefficient is never selected or graded on the role-group that fit it; selection uses the select and validate
  shares, never the held-out points. New sources draw fit, select and validate only.

1.5 **Proposal. Calibration acceptance gates (precommit, X8).** Before any fitting reads these sources, the numeric
gates are precommitted: the baseline each fit must beat; the error metric and its mandatory slices (engine, chip,
workload at least); the minimum sample count per slice for a verdict (at least `min_points`); the allowable
per-engine and per-chip regression elsewhere; the held/anchor verdict, evaluated once after selection; and the
revise-or-revert rule. The thresholds themselves are still to be set by the maintainer, and are a blocker on
fitting until they are.

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

3A.1 **The ledger follows each source.** Every row InferenceX publishes is ingested exactly once and assigned to
its canonical unit (duplicate and repeated records of one configuration fold into that unit, as the role-key rule
requires), not only the db-dump/2026-09-28 rows plus hand-pinned supplements. New rows are pinned by record id and content SHA-256, as
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

**Proposal (decided, colleague review).** Make the small-slice guard legible and unambiguous. A figure over fewer
than `min_points` (10) points reads as a contradiction with the per-point table below it, and the text covers most
fine slices. Decision: raw point rows stay visible at every `n`; an aggregate accuracy figure is **always withheld
below `min_points` at every level** — headline and every drilled-in leaf alike — and a withheld aggregate is
excluded from every verdict. (The earlier "stop applying the guard at a drilled-in leaf" idea is dropped: it let a
small slice look like strong evidence.) The threshold (10) stays, and a test pins the behaviour. Show the held
figure as its count (`n=3 · mean held`), not a bare verdict, and have the per-point table state the rule.
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

## 5. CI: a PR text edit must not change merge state

5.1 **Maintainer (2026-11-18).** File this for M3.2 in blis-design and in each repo's `ci.yml`:
- Editing a PR's title or body, without changing its base or head, must never change its merge state.
- The checks that read the text become their own required checks (for example `pr / description`), triggered on
  `edited` and nothing else.
- The heavy ci workflow and its required aggregate do not run on a text-only `edited` event. The retarget case is
  detected through `github.event.changes.base`, so it stays covered.
- A test or CI self-check must prove that a body edit leaves `mergeStateStatus` unchanged.
