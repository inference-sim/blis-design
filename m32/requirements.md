# BLIS M3.2 requirements (working capture, started 2026-11-18)

Status: being captured with the maintainer; more requirements to come. Not yet a design or plan.
**2026-11-18: the maintainer accepted the proposals in sections 1, 2 and 3** (1.2, 2.2-2.4, 3.2). 1.3 stays open.
**Section D (design changes) is a proposal under team review**; nothing in it is decided.
Each item says whose it is: **Maintainer** (stated or decided by the maintainer), **Proposal (accepted)** (a
proposal the maintainer accepted) or **Proposal** (open to correction).
Supporting evidence is in `evidence/` next to this file: what each project publishes (`INVENTORY.md`), where each
new source records its settings (`SETTINGS-PROVENANCE.md`), why so few points are scored (`COVERAGE-FUNNEL.md`),
how configiq rows are produced (`CONFIGIQ-FINDINGS.md`), and what the two requested models need on GB200
(`NEW-MODELS-GB200.md`).

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
- *The new data is pinned to engine commits, not releases.* Nearly every vLLM CI perf row names a vLLM commit
  (a few say `nightly` or a release tag), and every SGLang nightly names an SGLang commit (§1, §2.3). Today
  BLIS can model only a release, so it cannot fit against the exact engine code those runs used.

### D0. Terms used in this section

- **Engine upgrade.** Porting the diff of the code an engine module already models (scheduler, KV-cache manager,
  connectors, defaults, lowering) from one upstream commit to another. It changes behaviour for every model.
  "Port" and "move the modelled commit" mean the same thing here.
- **Model support.** Work in an engine module for one model, needed only when that model brings engine-facing
  code of its own (D1 lists the cases). It is separate from the upgrade.
- **Onboarding a model.** Up to three pieces of work, done after any engine upgrade the model needs:
  - *Catalog entry* (always): the model's `config.json`, its catalog entry, and a graph handler if the
    architecture is new. A new kind of layer also needs new graph vocabulary, and then the engine must learn to
    lower it, which makes the engine piece depend on this one.
  - *Model support* in the engine module, when needed.
  - *Coefficients*, required when a kernel the model runs on the target chip has neither a registry entry nor
    a coded fallback. The cost model refuses a missing coefficient rather than defaulting it
    (blis-substrate `kernel/new.go`: "A missing coefficient … is an error rather than a default"). A
    transferred or assumed entry, written by its family's writer script (SUB-4), makes the model run; a
    measured entry, fitted on fit units, makes it accurate.
- **Commit distance.** How far a run's engine commit is from the modelled one: commits apart, and releases
  apart where the two sit in different releases. Under D1 it is named on a point beside its grade, as the
  release difference is today (§3A.5); the G3 and G4 rule for a different engine build (COV-6) is unchanged.

### D1. Model any upstream commit, not only a release (vLLM and SGLang)

**Today.** An engine module models one upstream release (LIF-5). A build runs one release of each engine, and a
scenario that names another is refused (LIF-6). A run on another release is scored as a named release
difference (§3A.5, §11.5, COV-6).

**Proposal.**
- An engine module models one upstream **commit**: a release tag, or a commit on the upstream's main or release
  branch. The Upstream record names the commit and the release it descends from. A build still runs one commit
  of each engine, so LIF-6's refusal stays, with a commit in place of a release.
- An upgrade is ported as a diff, as v0.32.0 to v0.33.0 was. The generators (`fields.json`, `surface.json`,
  `kernel_impls.json`) already take the upstream reference as a parameter. The oracle environment is locked per
  commit.
- A point whose run used the modelled commit has no release difference. Any other point names its commit
  distance (D0).
- **Model backport**, the narrow case: the upstream commits that add one model are applied onto the modelled
  commit and listed in the Upstream record. A backport carries model code only, never scheduler, KV or connector
  changes, and folds away when the modelled commit contains it.
- **When to move.** On each upstream release, and on demand when a team scenario needs a later commit. Each move
  re-runs the oracle and the goldens.
- **Model support is needed** only when a model brings engine-facing code that an upgrade does not port, because
  it lives mostly in the model's folder (for example `vllm/models/inkling2/`):
  - a KV-cache layout the module has not seen, as DeepSeek-V4's sliding-window cache and compressor were
    (`core/kv/layers.go`);
  - its own kernels, or a backend choice the module does not lower, as Muse Spark's fused kernels were
    (blis-vllm#272);
  - a new drafting method or scheduler hook.
- A model that brings none of these needs no model support. Onboarding it is the catalog entry, plus any
  coefficients its kernels lack (D0).
- **Upgrade report.** Every engine upgrade generates a report of the models the new commit supports. For each
  model it gives:
  - whether the catalog has it;
  - whether it needs model support, and for what. This comes from the regenerated surface, field and kernel
    lists, which must give every new entry a status (X9), and from the model's own code paths;
  - for each catalog chip, the coefficients it lacks: those it cannot run without (no entry and no fallback),
    and those running on transferred or assumed values.
- The report is the to-do list for model requests, in advance. A run of the requested scenario gives the same
  answer for one model: a missing catalog entry is refused by name (`not_in_catalog`), an engine refuses what it
  cannot lower, a missing coefficient is refused with its name, and the Result records each coefficient's
  method. No separate preflight command is needed (D2).

**Effect.** A new model on upstream main can be supported (D4). The vLLM CI perf and SGLang nightly runs can be
fitted against the exact engine code that produced them (§1). A named release difference becomes a named commit
distance, which is finer.

### D2. Lowering out of blis-substrate, brought forward from M4

**Today.** The catalog's graph deriver still holds vLLM lowering. The plan moved its removal, and the
contract-change review set that removes `contracts/rules/` with model values moved into graph fields, from M3 to
M4 (2026-11-17). The design already says a graph holds only what the checkpoint states, and that sharding,
fusion, padding and the nodes emitted under a layout are lowering (SUB-15). It also says onboarding a model is
one blis-substrate pull request with no engine code (§12.1, T-M1). Neither holds yet, and the second can hold
only for a model that needs no model support or coefficients (D0).

**Proposal.** Bring both into M3.2.
- Move all lowering into the engine modules.
- Remove `contracts/rules/`, as the contract-change review set (§12.8).
- Drop the onboarding preflight command that §12.1 describes (`inference-sim onboard --plan`, never built). A run
  of the requested scenario, and the upgrade report (D1), answer the same questions.

**Effect.** A new architecture built from existing kinds of layer is onboarded with a graph handler plus data;
each engine lowers it with the lowering it already has. A new kind of layer still needs engine lowering (D0).

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
one Go module (SUB-13) is restated for the new layout. A model's catalog entry, model support and coefficients
(D0) become one pull request.

**What is given up.** The hard wall between repositories. A simulator change could edit catalog data in the same
pull request, so the lints and `CODEOWNERS` must do what the walls did. Each repository's merge rules, checks and
workflows have to be consolidated.

**Timing.** If adopted: at a release boundary, after the M3.1 cut, as the first M3.2 item, because D1 and D2 are
easier in one repository. The migration is not sized yet; a sizing from the actual workflows, checks and open
issues comes before the decision.

### D4. Support requested by a team: Mistral-Large-4 and Inkling-2-Small on GB200

**Request.** A GB200 configuration for both models on 16 GPUs (Muse Spark's capacity), for the team to use and
verify.

**Facts** (checked 2026-11-18; `evidence/NEW-MODELS-GB200.md`).
- **Mistral-Large-4.** `MistralLarge4ForCausalLM`, with a DSpark drafter. It is in vLLM v0.34.0, released
  2026-11-16, and on main; it is not in v0.33.0, which blis-vllm models. Its Hugging Face repository is gated.
- **Inkling-2-Small.** `Inkling2ForConditionalGeneration`, 594B. It is only on vLLM main, in vllm-project/vllm#67325,
  merged 2026-11-18 as `abb8194dc3`, and not in v0.34.0. Recent vLLM releases came about two weeks apart.
  blis-substrate#88 tracks it.

**Engine upgrade.** One modelled commit can serve both: a vLLM main commit at or after `abb8194dc3` carries both
models (D1). Without D1, Mistral-Large-4 comes with the v0.34.0 upgrade and Inkling-2-Small waits for v0.35.

**Onboarding, piece by piece (D0).**

| Piece | Inkling-2-Small | Mistral-Large-4 |
|---|---|---|
| Catalog entry | a branch of the existing Inkling handler; new nodes are of existing kinds (block attention residuals and MoE softcaps as elementwise nodes), and its DSpark drafter follows the catalog's other DSpark drafters | a new handler combining kinds the catalog has: DSA sparse attention (GLM-5), a layer reading another layer's KV and reusing another layer's indexer (DeepSeek-V4.1); to confirm from its gated `config.json` |
| New graph vocabulary | none expected | none expected |
| Model support | likely needed: it ships its own kernels (relative-position FA4 attention, a custom TRT-LLM batched GEMM for its MoE, its own all-reduce), which blis-vllm must lower | probably small: its KV sharing and sparse index groups are close to DeepSeek-V4.1's, to check against `core/kv` |
| Coefficients on GB200 | NVFP4 and MXFP8 grouped MoE GEMMs have no entry on any Blackwell part; at least transferred entries are required unless a coded fallback covers them (not yet checked). Relative-position attention is priced as plain attention | sparse-MLA attention has no GB200 entry (31 entries, all H100 and H200); the same applies. The MLA decode floor on GB200 is assumed |
| Drafter acceptance | borrowed | borrowed |

Because neither model brings a new kind of layer, the catalog entry and the engine pieces are independent of each
other. AISimulate's GB200 collection is the likeliest fit data for the missing coefficients; whether it covers
these two kernel families is not yet checked. If no source covers them, they are transferred or assumed (1.6), with
no new GPU runs.

**Answer to the team.** Give each configuration with its confidence. Neither model has measured runs on GB200, so
a configuration is a prediction with no held-out evidence, with its main costs on transferred or assumed values
until fitted. GB200 decode is about 1.35 times slow per token until blis-substrate#140 and blis-vllm#272 land
(§0.2).

### D5. Changes blis-design needs

The standing design and the release plan both change. Each item is one blis-design pull request to `main`,
except where items share lines.

| Design area | Change | For |
|---|---|---|
| §2 Shape, §2.2 ownership table, the repository tree | the four repositories become directories of inference-sim; `contracts/` its own module | D3 |
| §5 repository cards | merge the blis-substrate, blis-vllm, blis-sglang and blis-kvstore cards into inference-sim's, keep a card for the `contracts` module; restate each check's "Runs in" by directory | D3 |
| §6 engine boundary, X2, KVS-2 | the same rules, checked by an import-graph lint over directories | D3 |
| §7.1 engine port frame; §7.5 surface list (X9); §7.6 porting a framework before its features | an engine models an upstream commit; the model backport; the upgrade report from the regenerated lists | D1 |
| §8 lowering; SUB-15 | lowering lives only in engine modules; the deriver writes checkpoint facts only | D2 |
| §11.2 to §11.5, COV-6 | the named release difference becomes a named commit distance beside G3 and G4 | D1 |
| §12.1 onboarding; T-M1 | onboarding is up to three pieces (D0); "one pull request, no engine code" holds only for a model that needs no model support or coefficients; a run of the requested scenario and the upgrade report replace the `onboard --plan` command | D0, D1, D2 |
| §12.8 contract-change review set | one pull request in one repository, plus the router fork | D3 |
| §13 automation | the release bot without the pin cascade; path-filtered CI; the upgrade report | D1, D3 |
| §14 versions: LIF-2, LIF-4, LIF-5, LIF-6, §14.4; X10, X11; SUB-13 | an engine models one commit; one repository's release branches; pins only to `contracts` and the router fork | D1, D3 |
| The invariant registry (`contracts/invariants`) and its generated appendix | each record's "Runs in" and check names follow the new layout | D3 |
| The coefficient registry's scope rules | engine-path costs keyed by the identity of the code that does the work (§3.2, not part of D but a design change too) | §3.2 |
| The release plan | move the M4 lowering item into M3.2; add D1 to D4 to the M3.2 section; map the moved issues | D1 to D4 |

### How D relates to the rest of this document

- §1, §2: per-commit data matches per-commit engines (D1).
- §3.2: engine-path coefficients are keyed by the code that does the work. With D1, that code is pinned by
  upstream commit.
- §3A intro, §3A.5, §3A.9 and §3B use "release difference" and "release distance". Under D1 these read as commit
  distance (D0). They stay as written until D1 is decided.
- §0: the carried M3.1 items are unchanged. After D3, the re-pin cascades behind several of them go away.

### Open questions for the review

- **Q1.** D1: who decides an on-demand move of the modelled commit, beyond the move on each release?
- **Q2.** D1: does a backport need its own grade, or is commit distance enough?
- **Q3.** D2: should the `contracts/rules/` removal come into M3.2 with the lowering move, or stay in M4?
- **Q4.** D3: consolidate, or keep the repositories and remove the cascade with tooling (a local `go.work`, a bot that
  runs the cascade, and one CI job that tests every repository at the pull request heads)? Tooling keeps the
  walls, but cross-repository changes stay non-atomic.
- **Q5.** D4: M3.2, or a patch release of M3.1?

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
- *Borrowed acceptance named on stderr* (inference-sim#2079): done, inference-sim#2250 merged 2026-11-18 16:52 UTC.
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
- the all-reduce lane keyed by backend, part of blis-substrate#116 (blis-substrate#373); the GB200 value is still
  transferred (§0.5);
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
- Scored lanes for the internal studies (accuracy-dashboard#133 review): under 1.4 the internal experiments are
  training and validation data, so they get no accuracy lane. How well BLIS reproduces them is reported as a
  labelled training diagnostic (4.3).

**0.3 M3.1 plan issues the M3.1 set does not close.** Of the 189:
- 21 are already closed, and 26 close when the set merges;
- 36 are advanced but stay open (named with a `Part of` line; the bodies moved from 32 as items were added);
- 106 are not yet named by any of the seven bodies.

One mutually-exclusive outcome per issue, reconciling to the whole: 21 + 26 + 36 + 106 = 189.

Some of the 106 were advanced by item pull requests merged into the integration branches without a closing
line. Each is checked against the final bodies at the cut, and is closed there if it is done. The rest carry
into M3.2.

| Item | Advanced, not closed (16:55 UTC snapshot) | Not named: closing line at the cut (groups 1–2) | Not named: carries into M3.2 (groups 3–4) |
|---|---|---|---|
| P1 Release by commit | substrate #193, #343, #345 | – | sim #2145, #2149; substrate #204, #340 |
| P2 M3.0 review debt | substrate #335, #337 | substrate #338 | substrate #331, #332 |
| H1 Pull requests held from M3.0 | – | sim #1493, #1495, #2129 | sim #2052 |
| B1 Correctness | substrate #310; vllm #214 | sim #2214 | config-search #129, #133; dashboard #100; sglang #55, #91; sim #2152 |
| A1 Launch and step cost per chip | substrate #242; vllm #161, #191 | substrate #93, #115, #121, #136, #152 | substrate #114, #134; vllm #72 |
| C1 Dashboard coverage | – | – | dashboard #22, #58, #62, #63, #65, #79, #83, #87, #89, #90, #110, #111 |
| C2 SGLang end to end | – | – | sglang #32, #40, #44, #56, #57, #62, #63, #64, #65, #66, #67, #68, #70, #71, #73, #74, #75, #76 |
| S1 Every capability sweepable | config-search #93, #125, #138 | – | – |
| R1 Command-line surface | – | – | sim #2216 |
| A2 Time before the engine, and prefill | – | sim #2094 | substrate #94 |
| A3 KV capacity and memory | sim #1969; substrate #255, #281; vllm #73, #129, #158 | substrate #76, #294 | substrate #73, #132 |
| C3 Closeness grades | – | – | dashboard #53; sim #2101, #2103; substrate #41, #43 |
| C5 Catalog by points blocked | substrate #317 | substrate #245, #258 | dashboard #7; substrate #91, #105, #106, #109, #126, #179, #188 |
| A4 Collectives and MoE paths | substrate #150; vllm #75 | – | substrate #118, #123; vllm #74, #108 |
| A5 Speculative acceptance | substrate #125, #164 | sim #2079, #2115 | dashboard #59, #80; sim #2125, #2136, #2141, #2142; substrate #144 |
| T1 Data-parallel serving and network structure | sim #2126; substrate #48, #49, #346; vllm #64 | substrate #161 | dashboard #61, #64, #91; sim #1988, #2146, #2164; substrate #50, #51, #153 |
| T2 KV tiers under P/D | vllm #47, #132, #146 | sim #2202, #2203; vllm #184, #204 | vllm #190 |

The two right-hand columns come from [`m31-carried.tsv`](m31-carried.tsv) (106 issues: 22 need only a closing
line, 84 carry into M3.2). The advanced column is the 16:55 UTC snapshot, 32 of the 36 now advanced.

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
  estimate for the custom lane. Use a measurement of the GB200 4- and 8-rank custom all-reduce if one of the
  allowed sources holds it; otherwise the value stays transferred, with its source and rationale, and the points it
  prices name it (1.6). Keep #116 open until a measured value exists.

## 1. New data sources for calibration

1.1 **Maintainer.** Bring these data sources into BLIS properly for calibration:
- SGLang nightly profiler traces, `github.com/sgl-project/ci-data` (step and host overhead, kernels);
- the vLLM CI perf API, `ci.vllm.ai/api/perf`, with the `vllm-project/perf-eval` recipes (current vLLM on H200 and B200);
- SGLang nightly job logs and `consolidated-metrics` artifacts (scheduler behaviour, resolved server arguments).

1.2 **Maintainer.** Licence is not a blocker: the data is queried, not redistributed.
**Proposal (accepted).** So none of it is committed to a public repo (standing-design rule D6). Units are built from a pinned fetch at fit
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
  come only from those. Here "held-out" means both shares: the published headline is computed on anchor units,
  and held units are evaluated once per pre-registered change and reported with that change (standing-design §10).
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

1.6 **Maintainer (2026-11-18). No new GPU or cluster experiments, with no exceptions.** M3.2 fits, selects,
validates and evaluates only on data that already exists: the sources of §1 and the ones it adds. Where no source
measures a coefficient, it is transferred (from another chip, width or lane, by a stated rule) or assumed (with its
reasoning), written by its family's writer script, and named on every point it prices. It is replaced when data
appears. A test that compares against real runs uses runs already recorded (for example blis-vllm#305). This
applies to D4's missing GB200 coefficients too.

## 2. Settings identification (apples to apples)

2.1 **Maintainer.** For every point used, it must be easy to find out the run's settings: workload,
cluster, GPU type, model and engine settings. Getting these right is what makes the comparison like for
like. Identifying the settings correctly is part of the M3.2 calibration process, not a one-off.

2.2 **Proposal (accepted).** Follow the standing rule: every value comes from the run's own records; a value no
record holds is a named substitution with its source and lowers the grade; never a BLIS default. Each
source's scenario writer has a test that checks every field against the record it came from.

2.3 **Proposal (accepted).** Per source, the record that settles each setting (from SETTINGS-PROVENANCE.md):

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

2.4 **Proposal (accepted).** Values to confirm before any fit: the statistic `aggregate_perf.py` uses over
repetitions; `vllm bench` seed and range ratio at each commit; how the recipe's revision is matched to a
row's date when the recipe changed that day.

## 3. Which engine the data improves

3.1 **Maintainer.** Use calibration to improve both SGLang and vLLM as much as possible. Data that can only
improve one engine (because of the fit-the-engine-you-predict match) is still used, not ignored. Some
coefficients are shared and others are not, and that is fine.

3.2 **Proposal (accepted).** Kernel coefficients stay keyed by kernel implementation, so SGLang data fits vLLM's
value wherever both run the same implementation. Engine-path costs (host, scheduler, launch, CUDA-graph
replay) get keyed by the identity of the code that does the work, so each engine has its own value
without an engine name in substrate (X2). Today host overheads are scoped by hardware and model only; this
is a design change that lands before the plan.

## 3A. Maximise scorable coverage

**Maintainer.** Don't leave scorable points on the table: maximise coverage, especially for InferenceX. Today
199 of 20,364 InferenceX anchors are scored (nightly 2026-11-17, v0.17.1), and about 213 of 1,702 configiq
units can be simulated. The funnel and its evidence are in `evidence/COVERAGE-FUNNEL.md`:
the losses are mostly policy and a frozen ledger, not missing data.

**Proposal (accepted, 2026-11-18).** Older points count in the headline
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

3A.2 **Maintainer (2026-11-18). No age limit on scoring.** The 180-day window stops being a gate: every anchor whose inputs can be
recovered is scored, at its grade. It removes 12,491 in-scope anchors today, as their only reason. A date range
becomes a slice (3B).

3A.3 **Recover inputs from durable records, and keep the ones that expire.**
- vLLM single-turn: the API's `/server-log` (verified 200 for rows from 2026-02 and 2026-03).
- SGLang and P/D: the job log while GitHub holds it, else the recipe or script at the run's commit (the pull
  already does this).
- Measurements the API has superseded: the dump.
- Inputs that expire (GitHub job logs and artifacts, about 90 days; agentic exports): archived privately as they
  are pulled, never committed publicly (standing-design rule D6), so a point stays re-scorable after the source deletes them.
A point whose inputs are truly gone is G5 with a reason that says which record is gone.

3A.4 **Engine and table gaps, ranked by points held back.**
- SGLang: scored from M3.1's blis-sglang field list (186 in-window anchors blocked today, 109 by that alone; about
  2,950 in-scope SGLang and Dynamo-SGLang anchors in all, about 5,400 with AMD parts, nightly 2026-11-18).
- The router table maps Dynamo's router (252 in-window anchors).
- The not-modelled settings tail (`data_parallel_rpc_port`, NCCL and FlashInfer environment variables,
  `use_trtllm_attention`, `moe_backend`, ...): each is modelled, proven inert, or given an estimation rule, in
  order of the points it alone holds back.
- TRT-LLM stays refused: BLIS has no TRT engine.

3A.5 **Older engine releases are scored, not refused.** A run on a release other than the one an engine repo
models is a named release difference at a lower grade (the existing rule), for both engines.

3A.6 **Coverage is reported as a funnel for InferenceX and configiq**, every release: held by the source, units, in
scope, inputs recoverable, scored, by grade, with the top blockers by points they alone hold back. The new
sources (1.4) get a training-coverage count instead: rows held, units, inputs recoverable, used in a fit. A drop at any stage
is a visible number, not an absence.

3A.7 **configiq.** Waiting on the configiq team's answers (the maintainer asked them). Meanwhile their repos
are being read to recover each setting (§3C).

3A.8 **Expected effect** (maintainer's expectation, 2026-11-18; the shares stay the same, the counts rise).
The role proportions do not change: for new units, 30 fit, 10 select, 10 validate, 30 held and 20 anchor, and
legacy units keep their sides. The held-out points grow because the same proportions now apply to far more
scorable points. Upper bounds from the 2026-11-17 nightly and the ledger:

| | Today | M3.2 ceiling | What opens it |
|---|---|---|---|
| InferenceX anchors scored | 199 | about 2,800, up to about 4,700 | the 199; the 381 non-TRT unscored in-window anchors; out-of-window anchors measured from 2026-02 on (1,143 vLLM-family, 850 SGLang-family); about 240 non-TRT anchors among the 1,287 rows published after the dump (20% of 1,215); up to 1,913 more SGLang-family anchors from before 2026-02 if their recipes at the run's commit still resolve. TRT stays refused. |
| InferenceX held units | not counted on the dashboard | about 1.5 times the anchors | the same levers; held is 30% against anchor's 20% for new units |
| configiq held-out units | not yet published (below) | about 850 of 1,702 (50%) by proportion; about 185 of the 373 forge-written H200/B200 units | §3C's family rule |

These are ceilings, not forecasts. The real count depends mostly on how many old runs' inputs can still be
recovered. The API serves only the latest measurement per configuration, and in M3.1, 213 of the 573 vLLM points
of AISimulate's matched set had their record gone (404). That 213 is unrelated to configiq's 213 eligible units.

**Measured 2026-11-18:** the API's `/server-log` was queried for 33 vLLM single-turn records that only the dump
holds, three per month. Every record from 2025-09 to 2026-01 returned 404, and every record from 2026-02 to
2026-07 returned 200. So the 3,758 vLLM-family anchors measured before 2026-02 cannot be rebuilt from their
logs. They stay G5 with that reason unless another record of their settings is found. SGLang points take their
launch command from the recipe at the run's commit, not from this endpoint, so the older SGLang anchors are
counted as "up to" until that path is checked. The count also depends on the Dynamo router mapping and the
not-modelled settings tail. **Proposal:** measure it first, with a pull of every anchor that only checks whether its inputs can be
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
- *Grade and route by release difference.* Old-release dump runs carry the 3A.5 named release difference. Under
  1.4's draw, their fit, select and validate shares feed calibration. Their anchor share counts in the headline at
  its grade (3A, the maintainer's decision), their held share in pre-registered evaluations (1.4), and the
  same-release figure is a slice (3B).
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
- engine, engine release or commit, and its distance from the modelled one (release difference today, commit
  distance under D1);
- topology (TP, DP, EP, P/D pools), speculative method, offload and KV tiers, router;
- workload type, ISL/OSL, concurrency, arrival process, prefix sharing;
- measured date;
- grade and each substitution named on the point.
Each slice shows its point count and coverage beside its accuracy, so a small slice can't pass for a strong
result.

**Proposal (accepted, colleague review).** Make the small-slice guard legible and unambiguous. A figure over fewer
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

3C.1 **Classify each row by writer.** Counts are on the current dataset revision (1,710 whole-run units); the
ledger's pinned revision has 1,702 (3A). Family A is forge, recognised by a `/v1/...` request type and prefix caching
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

3C.7 **Ask Red Hat**, beyond the questions the maintainer already sent (3A.7; the maintainer owns this
conversation):
- publish an allow-listed `runtime_args`, the image tag, the GuideLLM version, the cluster tag, the start and end
  times, DP and the turn index;
- fix the case mismatch that drops DP;
- publish more of the roughly 52 models the CSV holds.

## 4. Proposals not yet discussed

4.1 Start harvesting the 90-day sources now (SGLang job logs and metrics artifacts; Tritonbench if §1.3 brings it
in), before M3.2 starts, so the window keeps growing instead of rolling off. The plan lists this as a
prerequisite.
4.2 *Superseded by 3A.5 and 1.4:* InferenceX and configiq runs on other releases are scored with a named release
difference (3A.5); the new sources are fitted, never scored.
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
