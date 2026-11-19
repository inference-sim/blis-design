# BLIS M3.2 requirements

These are the working requirements for M3.2, the release after M3.1, captured with the maintainer from
2026-11-18. They are not yet a plan, and more will be added. The design they build on is
[design v2.1.0](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html).

**Labels.** Each item says whose it is:
- **Maintainer**: stated or decided by the maintainer.
- **Proposal (accepted)**: a proposal the maintainer has accepted.
- **Proposal**: open to correction.
- **Open**: a question no one has decided.

Section DC records the design changes that design v2.0.0 adopted, and lists what M3.2 builds for them. It comes
first because the maintainer asked that design changes be the first requirement. It cites later sections.

**Evidence.** The notes in `evidence/`, next to this file, back the figures:
- what vLLM, SGLang and PyTorch publish as performance data (`INVENTORY.md`);
- where each new source records its run settings (`SETTINGS-PROVENANCE.md`);
- why so few InferenceX and configiq points are scored (`COVERAGE-FUNNEL.md`);
- how configiq rows are produced (`CONFIGIQ-FINDINGS.md`);
- what the two models a team requested need on GB200 (`NEW-MODELS-GB200.md`);
- the implementation particulars the design v2.0.0 audits moved out of the design (`DESIGN-V2-PLAN-ITEMS.md`).

Figures are as of 2026-11-18, except the M3.1 status in §0, which is as of 2026-11-19 04:10 UTC. Every repository named here is under
`github.com/inference-sim/` unless another owner is shown.

## Terms

**Repositories.** Design v2.0.0 has one simulator repository and the router fork. M3.2 builds that layout (DC3).
Until the migration lands, the three repositories below still exist, and the issue numbers in this file name them.
- **inference-sim**: the simulator. Its tagged release is the only one a milestone requires (v0.18.0 is M3.0,
  v0.18.1 is M3.1). Since M3.1 the other repositories are pinned by commit, and their tags are optional.
  After the migration it also holds the three below, as `substrate/`, `engines/vllm` and `engines/sglang`.
- **blis-substrate** (`substrate/`): the shared contracts (`contracts/`), the cost model (`kernel/`), the model
  catalog (`catalog/`), the coefficient registry (`registry/`) and the ledger (`catalog/ledger/`).
- **blis-vllm** and **blis-sglang** (`engines/vllm`, `engines/sglang`): Go models of the vLLM and SGLang engines,
  each ported from one upstream commit. Each is an **engine module**.
- **The router fork**: inference-sim's fork of llm-d's router (`llm-d-router`, branch `llm-d-r`). It owns the
  hosting contract and depends on no BLIS module.
- **accuracy-dashboard**: scores simulated runs against measured runs and publishes accuracy.
- **blis-config-search**: searches deployment configurations with the simulator.
- **blis-design**: the design (`main`) and these requirements (branch `m32`).

**Data sources.**
- **InferenceX**: SemiAnalysis's public end-to-end serving benchmarks, with server logs and recipes.
- **configiq**: Red Hat's public dataset of GuideLLM results for upstream vLLM releases. GuideLLM is a load
  generator for LLM servers.
- **AISimulate**: NVIDIA's operator sweeps (one kernel at a time over many shapes) and forward-pass measurements.
- **forge**: Red Hat's open-source benchmark launcher (`openshift-psap/forge`), which wrote most of configiq's
  recent rows (§3C).
- **AgentX**: an agentic workload of recorded coding-agent sessions that InferenceX and the internal experiments
  replay.
- **The internal experiments**: the team's own measured runs of its target scenarios. Their data is private; it is
  never published, and no public text says which runs it holds.
- **The dashboard nightly**: accuracy-dashboard's nightly job, which scores the ledger's anchor units on the latest
  simulator release. (SGLang's own nightly CI is a different thing, and is always named as SGLang's.)
- **The dump** is InferenceX's database dump `db-dump/2026-09-28`, which the ledger pins; its date is the
  **cutoff** between dump rows and supplements. **Supplements** are
  InferenceX rows published after the dump and added to the ledger one by one, each pinned by its row id and the
  SHA-256 of its content.

**Design rules and sections.** IDs such as X7, SUB-15, LIF-5, COV-6, T-M1 or D6 name rules of design v2.1.0. The
letters group them: X across components, SUB substrate, LIF versions and releases, COV accuracy coverage, VAL
coefficients, D the ledger, T a trigger's test. Each citation here says what the rule requires where that matters.
A design section is written "design §n". A bare § number is this file's own section (§0 to §5, §3A to §3C); the
design changes are DC1 to DC5, without a §.

**The ledger and roles.**
- **Ledger**: blis-substrate's list of every measured unit from every data source, with each unit's role
  (`catalog/ledger/`).
- **Run**: one execution of a benchmark against a deployment, as a data source records it. One InferenceX run can
  measure several concurrencies; each becomes its own unit.
- **Row** and **records**: a row is one line a source publishes (an InferenceX API row, a configiq CSV row); a
  run's records are everything its source keeps about it: rows, server log, recipe and launch command.
- **Scenario**: the simulator's input describing one run to simulate: the deployment, the cluster and the workload.
- **Unit**: one ledger entry. For InferenceX it is one configuration at one concurrency from one benchmark run,
  with every measurement of it. A **point** is a unit as the dashboard scores it.
- **Role**: each unit has one role, drawn once by a seeded rule: **fit**, **select**, **validate**, **held**,
  **anchor** or **report**. A report unit gives context only and never yields a number. The draw is per **role key**, so units that are near-copies share a role. For
  InferenceX the role key is the source, model, hardware, precision, framework, benchmark type and configuration
  hash; it leaves out the recipe fingerprint, the concurrency, the measured date and the benchmark run. For
  configiq it is every identifying field except the concurrency.
- For new InferenceX and configiq units the draw is 30% fit, 10% select, 10% validate, 30% held and 20% anchor.
  Units from older ledger revisions were first split into a fit group and a held group. They stay in that group, and
  the ledger's rules split each group into roles (fit and select; held and anchor).
- **Training data**: every unit whose role is fit, select or validate, and all data from sources with no held-out
  roles. Fit units fit coefficients, select units choose between fits, and validate units check a fit.
- **Held-out shares**: held and anchor. **Anchor** units make the published **headline**, the dashboard's
  accuracy figure. **Held** units judge a pre-registered change, with one evaluation per pre-registration
  (design §10.2). Pre-registering a change means committing its hypothesis and gates before any held-out data is
  read (design §12.3).

**Grades.** How closely a point's simulated setup matches its run. The grade table below gives the five grades.

**Grade table. G1 to G4 are scored grades; G1 needs the run's own engine commit, every setting it sets modelled or
proven inert, and every coefficient measured or calibrated.**

| Grade | Meaning (design §11.3) |
|---|---|
| G1 exact | the run's engine commit is the one the scoring release models; every setting the run sets is modelled or proven inert; every coefficient is measured or calibrated; the simulated requests are the ones the run sent |
| G2 estimated | as G1, except for named exceptions, such as a transferred or assumed coefficient, a named substitution, or a router mapped through the router table |
| G3 other commit, same code | the run used another commit, and none of the upstream functions the engine module ports changed between the two |
| G4 other commit, changed code | as G3, but some ported functions changed, or the build is nightly or custom |
| G5 not scored | with a named reason |

- **Named substitution**: a value no record of the run holds, stated on the point with the value used and its
  source. It lowers the grade. An **estimated substitution** is a named substitution whose value comes from a
  stated rule rather than a record.
- **Commit distance**: how far a run's engine commit is from the modelled one, counted from their merge base:
  commits apart, and releases apart where the two commits are in different releases (design §11.3). A point on
  another commit names it (§3A.5).

**Coefficients and engines.**
- **Coefficient methods** (design §9.2), from most to least trusted: **measured** (fitted to microbenchmarks of
  that exact kernel implementation on that chip), **calibrated** (a physical formula with one or two factors fitted
  to end-to-end or forward-pass data), **transferred** (measured on a related implementation or chip, moved by a
  stated rule), **literature** (a cited published figure), **vendor_spec** (a datasheet figure), **roofline**
  (computed from catalog facts with a default efficiency from the same family) and **assumed** (a stated assumption
  with its reason). For each lookup the cost model uses the most trusted entry the registry has for that chip, and
  records its method.
- **Primitive family**: the coefficients that price one kind of operation, such as dense GEMM, decode attention or
  all-reduce.
- **Lane**: the kernel implementation a coefficient is fitted on, such as NCCL's all-reduce or a custom all-reduce.
  The dashboard's per-engine groups are called groups here, not lanes.
- **Lowering**: turning a model's graph (what its checkpoint states) into the operations one engine runs on one
  layout: sharding, fusion, padding, and the nodes it emits. A **graph handler** is catalog code that builds one
  model family's graph from its `config.json`. The **graph vocabulary** is the set of node kinds a graph may use.
- **Oracle**: an engine module's harness that runs the real upstream code with only the transport and the clock
  replaced, to check the Go model against it. **Goldens** are the oracle's recorded outputs. The **byte gate**
  checks that a refactor leaves simulator output unchanged, byte for byte.
- **TRT-LLM**: NVIDIA's TensorRT-LLM serving engine, which BLIS does not model. **vLLM-family**, **SGLang-family** and
  **TRT-LLM-family** group InferenceX's frameworks by the engine underneath, as `evidence/COVERAGE-FUNNEL.md` Table F2
  lists them (for example, the vLLM family includes Dynamo and llm-d deployments of vLLM).
- **P/D**: prefill/decode disaggregation, where separate GPU pools run the prefill and decode phases.
- **Abbreviations**: TP, DP and EP are tensor, data and expert parallelism. TTFT is time to first token, TPOT time
  per output token, ITL inter-token latency. ISL and OSL are input and output lengths in tokens. MTP is multi-token
  prediction, a form of drafting.
- **Router table**: the substrate's map from a router a run used, such as Dynamo's, to the nearest policy llm-d's
  router offers.
- **Age limit**: the dashboard's rule, today, that scores only runs measured in the last 180 days (§3A.2).
- **Funnel**: the count of units at each stage from the source to scored (§3A.6). **Slice**: the subset of points
  that share an attribute value, such as one chip (§3B).
- **Speculative decoding** uses a small **drafter** model to propose tokens. **DSpark** is one drafting method.
  **Acceptance** is the share of drafted tokens the target model keeps. An **acceptance profile** is the substrate's
  measured acceptance curve for one drafter and model.
- **Muse Spark**: a model in the catalog (its open checkpoint is Muse-Spark-Open). **TEP8** and **DEP8** are two of
  the 8-GPU layouts its scenario files use: TEP8 shards attention with 8-way tensor parallelism and the experts with
  expert parallelism; DEP8 runs 8 data-parallel ranks, with expert parallelism for the experts.

**Engine work and onboarding** (design §12.1, §12.4 and §12.5).
- **Engine upgrade**: porting the diff of the code an engine module already models from one upstream commit to
  another. It changes behaviour for every model.
- **Model support**: work in an engine module for one model, needed only when that model brings engine-facing code
  of its own, such as a KV-cache layout, its own kernels or a drafting method the module has not seen.
- **Onboarding a model**: a catalog entry, always; model support, when needed; and coefficients, needed only for
  a new primitive family. The substrate carries an assumed entry for every catalog chip in each family without a
  roofline formula, so every kernel can be priced (VAL-2). Fitted entries raise accuracy and are optional.

## DC. Design changes, adopted in design v2.0.0

**Status.** Design v2.0.0 ([the design](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html))
adopts the design changes this section first proposed on 2026-11-18. The design now states the rules and the
procedures. This section keeps each decision in one statement and lists, in one place, what M3.2 builds for it. Its
Appendix C maps every v1.0.0 rule to its place in v2.0.0. M3.2 implements design v2.1.0, which adds the
simplifications at the end of Table DC; rule IDs and sections cited here are those of v2.1.0.

**Why.** Changes crossed repositories in sequence: the per-pool offload fix took blis-substrate#402, blis-vllm#302
and inference-sim#2252, one after another, with full CI at each. And the new data (§1) is pinned to engine commits,
not releases, which BLIS could not model.

### The decisions

**DC1. An engine module models one upstream commit, not only a release.**
A run on the modelled commit is the same build and can be graded G1 or G2. A run on any other commit names its
commit distance and is graded G3 or G4. A model that lands upstream between upgrades is added as a model backport,
which carries model code only. An engine upgrade produces an upgrade report of the models the new commit supports.
In the design: [§2.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s2-2) Table 1
(engine modules), [§7.1](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s7-1),
[§11.3](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s11-3) (grades),
[§12.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-4) (engine upgrade, upgrade
report) and [§12.5](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-5) (model
support, backport); LIF-5, LIF-6, COV-6, T-E1 to T-E6, FID-14. A maintainer with write access decides an on-demand
upgrade and records it in an issue (design §12.4). A backport is graded by commit distance (design §12.5).

**DC2. Lowering lives only in engine modules.**
The catalog's graph deriver writes checkpoint facts and nothing else. The `onboard --plan` command is not built:
simulating the requested scenario and the upgrade report answer the same questions. The substrate has no rule
layer, so `contracts/rules/` is removed. A model that needs no model support and no new primitive family is
onboarded by one catalog pull request. In the design: SUB-15, SUB-12,
[§12.1](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-1) with T-M1 and T-M2.

**DC3. blis-substrate, blis-vllm and blis-sglang become directories of inference-sim.**
They are packages of inference-sim's one Go module (`substrate/`, `engines/vllm`, `engines/sglang`). The router fork,
accuracy-dashboard, blis-config-search and blis-design stay separate. The router fork owns the hosting contract and
its conformance suite, so it depends on no BLIS module and inference-sim imports it without a cycle. In the design:
[§2.1](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s2-1) and
[§2.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s2-2) Table 1,
[§3.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s3-2) (layout),
[§3.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s3-4) (checks by directory),
[§5.3](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s5-3) (the router fork),
[§14.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s14-4) (release branches); X7, X11,
SUB-1, SUB-13, RTR-3. The bottom-up merge order (X10) is retired. Review ownership is maintainer practice: no
`CODEOWNERS` file and no custom automation (maintainer, 2026-11-19).

**DC4** is an M3.2 requirement, not a design change; it follows the build list below.

**DC5. The standing design.** Every design change DC1 to DC3 needed is in v2.0.0, including engine-path
coefficients keyed by the identity of the code that does the work ([design §9.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s9-2), VAL-8; this file's §3.2). The review questions are closed:
Q1 and Q2 by design §12.4 and §12.5, Q3 by SUB-12 (the removal is in M3.2), Q4 by DC3 (consolidate), and Q5 by the
maintainer (DC4 is in M3.2). What remains is the release plan: move the M4 lowering item into M3.2, add the build
list below and DC4 to the M3.2 section, and map the moved issues (§0, `m31-carried.tsv`).

### What M3.2 builds for DC1 to DC3

**Table DC. M3.2 implements the adopted design; each row is work, not design, and the last column names the
design rule it serves. Order: the migration first, because the other groups are easier in one repository.
Implementation particulars with their full wording are in `evidence/DESIGN-V2-PLAN-ITEMS.md`.**

| Group | What M3.2 builds | Rule |
|---|---|---|
| **Migration (DC3), in this order** | | |
| Sizing | Size the migration from the actual workflows, checks and open issues before it starts. It is not sized yet | |
| Hosting contract | Move `contracts/embed` and `contracts/conformance/embedtest` (about 2,300 lines of Go; 12 commits of history touch them) into the router fork as new files in `blisembed/`. New files cost none of the fork's patch budget (`hack/hosting-lint/budget.txt`); the edits to its `go.mod` and `go.sum` do. The fork's import test (`TestImportsOnlySubstrateContracts`) then forbids every `github.com/inference-sim/` package. Update the checks that name blis-substrate as the contract's home: `hack/embed-apidiff.sh` and its test, `hack/fork-policy/main.go` and `.github/workflows/hosting-lint.yml` in the fork; `contracts/architecture_test.go` and the SUB-1 API-diff check in blis-substrate. The conformance suite runs in the fork's CI. inference-sim imports the contract through its one `replace`, under llm-d's module path (`github.com/llm-d/llm-d-router/blisembed`) | X7, X11, SUB-1, RTR-3 |
| Subtree merge | Merge blis-substrate, blis-vllm and blis-sglang into inference-sim as `substrate/`, `engines/vllm` and `engines/sglang`, with a subtree merge that keeps their history. Every moved directory becomes a package of the one Go module | SUB-13 |
| Issues | Transfer the open issues of the three repositories and map the old numbers to the new. Re-map §0 and `m31-carried.tsv` when they land | |
| Checks | Replace the repository boundaries with an import-graph lint over directories (`go list`, required in CI) and the path-reference lint of X7. Consolidate each repository's merge rules, checks and workflows. Make heavy CI path-filtered, so a change runs only the jobs of the directories it touches. Restate each invariant's "Runs in" by directory in `substrate/contracts/invariants`. Add the module-size check | X2, X7, SUB-13, [§3.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s3-4) |
| Releases | Per-engine release branches become release branches of inference-sim, which already cuts `release-v0.18`. Re-point the pins of accuracy-dashboard and blis-config-search | [§14.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s14-4), X11 |
| Retire | Archive blis-substrate, blis-vllm and blis-sglang with a pointer to inference-sim, once the issues are transferred | |
| **Lowering (DC2)** | | |
| Deriver | Move all vLLM lowering out of the catalog's graph deriver into `engines/vllm`; the deriver writes checkpoint facts only, and its `--check` and rederivation test stay | SUB-15 |
| Rules layer | Remove `contracts/rules/` and move model values into graph fields; each engine module's refusal is the engine layer of validation | SUB-12 |
| **Any commit (DC1), all engines** | | |
| Generators | Make `gen_surface.py`, `gen_kernel_impls.py` and `gen_fields.py` work at any commit. Today `gen_surface.py` refuses a checkout at another commit, `gen_kernel_impls.py` needs one `kernels/<tag>/attention.json` per release, and `gen_fields.py` holds release-specific paths. Lock the oracle environment to the commit | X9, FID-2, T-E3 |
| Upgrade report | Generate the report of §12.4 (surface diff, field demand, source diff, and for each model the catalog entry, model support and missing coefficients). Every new surface entry gets a status. The dashboard uses the same diff generator to grade a run. Include the Transformers-backed fallback paths of vLLM and SGLang as surface-list items, and list the models that run only through them | X9, [§12.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-4), [§11.3](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s11-3) |
| Commit identity | Name commits in `stack.json` and in the scenario refusal; accept an on-demand commit in the release watcher; grade by commit distance in the dashboard | LIF-6, SIM-3, COV-6 |
| Backports | List backported commits in the Upstream record and check that every catalog model that does not use one has identical plans and traces with and without it | FID-14, T-M5 |
| **vLLM (`engines/vllm`)** | | |
| Tuned MoE configuration | Lowering selects the per-device fused-MoE configuration file that vLLM selects, and hashes it into the kernel's `CodeHash`. A run is G1 only when its tuned configuration is the one BLIS selected | [§9.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s9-2), G1 |
| Defaults at two commits | `gpu_memory_utilization` changed its default between commits. The diff generator reads defaults, constants and registry contents at any two commits, so that G3 compares a run's resolved defaults with the modelled commit's | FID-14, G3 |
| Platform preferences | Use a faked-device CUDA platform class for the block-size preferences, instead of transcribing them | FID-1 |
| KV events | Settle full-block and partial-block KV-event emission under each report mode from the block pool and coordinator source at the modelled commit, and record it in the surface list | [§7.5](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s7-5) |
| Step boundary | Record the step N+2 behaviour under asynchronous scheduling in the declared step boundary | DEV-3 |
| Backport paths | Record in the Upstream record the model directories, config parsers and architecture registry that a backport may change | [§12.5](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-5), FID-14 |
| **SGLang (`engines/sglang`)** | | |
| P/D allocation | The setting is `disaggregation_decode_allocation_policy`, `early` (the default) or `prefill_complete`. The port reproduces both, and the surface list records the setting and its default | SGL-3, [§6.4](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s6-4) |
| Radix-tree core | The Rust core is the default. The oracle runs both cores, the Go port follows the default, a T2 differential case compares them, and the surface list names their divergences | FID-2, SGL-1 |
| Surface list | Record the admission look-ahead ratio (`new_token_ratio`), maximum prefill tokens, retraction, output limits, maximum running requests under speculative decoding, KV-event hashing, the radix cache and drafter lists, and the NIXL storage-plugin mapping at the modelled commit | SGL-3, [§7.5](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s7-5) |
| **Substrate and simulator** | | |
| Code identity | Generate `code_paths.json` (the closure of engine-path code that each host, scheduler and graph cost depends on) for both engines, and add `CodeID` to `HostPlan` and `GraphPolicy`. This is the key for engine-path coefficients (§3.2) | [§9.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s9-2), VAL-8 |
| Host CPU | Add the `host_cpu` fact to node packaging (x86 hosts for H100 and H200, Grace for GB200) and scope engine-path coefficients by it | SUB-3, [§9.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s9-2) |
| Kernel lists | Generate each engine's `kernel_impls.json` as an engine-neutral copy under `substrate/registry/inputs/` with a freshness check, and move the VAL-8 cross-check into a simulator-package test. Connector and backend names of the vLLM and SGLang KV trees live only in each engine's surface list | X7, VAL-8, [§7.5](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s7-5) |
| Cross-generation transfer | Validate the GB200 (Blackwell) to Hopper transfer rules (leave one generation out) before use. Until then a cross-generation transfer ranks as roofline | VAL-5, [§9.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s9-2) |
| Ledger multiples | Record InferenceX's client multiples (10 measured, 2 warm-up, 12 in all) for `measurement_contaminated` in the ledger's source record | [§10.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s10-2) |
| **Simplifications (design v2.1.0)** | | |
| Simulator commands | Remove the `ledger`, `invariants` and `compose` commands from inference-sim, with their tests and docs pages, and the `blis invariants` mention in the README. Nothing calls them: the dashboard reads the ledger from the release checkout, and the substrate's own tool renders the invariant blocks | [COV-2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s11-9), X29, DEV-7 |
| Ledger embedding | Stop embedding `catalog/ledger/published/` in the simulator's data; the loader ignores everything under `catalog/ledger/` | [§3.3](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s3-3), [§10.2](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s10-2) |
| Dashboard nightly | Delete the stale "TEMPORARY until `blis ledger --list anchor`" comment in `api-nightly.yml`. It already reads the anchor list from the pinned checkout | COV-2 |
| Gated-config nightly | Delete the substrate's `nightly-fetch-configs.yml` and its entries in `.github/check-runs.yaml`; remove the `config-fetch` environment and its `HF_TOKEN` secret. Keep `fetch_pinned_configs.py` and `derive_graph.py --check --fetched`, which a maintainer runs. Add the gated-model step to the catalog README and a checkbox to the pull-request template, outside the generated block | X12 |
| **A future engine (TensorRT-LLM)** | The first cases for the native-code step of [§12.6](https://inference-sim.github.io/blis-design/v2.1.0/blis-target-design.html#s12-6). Not built in M3.2; the sites are recorded in the evidence file: the eviction policy's steady-clock read, the `getenv` of the window-size shares, the native and Python capacity schedulers (the oracle runs both), the pool allocation sites, an instrumented build for branch coverage, and a per-layer launch and shape dump for the engine-plan path | FID-1, FID-2, FID-4, FID-7, FID-11 |

### DC4. Support requested by a team: Mistral-Large-4 and Inkling-2-Small on GB200

**Maintainer (2026-11-19).** This is an M3.2 requirement, not a design change and not a patch release of M3.1.

**Request.** A GB200 configuration for both models on 16 GPUs, the capacity Muse Spark uses, for the team to use
and verify.

**Facts** (checked 2026-11-18; `evidence/NEW-MODELS-GB200.md`).
- **Mistral-Large-4.** `MistralLarge4ForCausalLM`, with a DSpark drafter. It is in vLLM v0.34.0, released
  2026-11-16, and on vLLM main. It is not in v0.33.0, which blis-vllm models. Its Hugging Face repository is gated.
- **Inkling-2-Small.** `Inkling2ForConditionalGeneration`, 594B parameters. It is only on vLLM main, added by
  vllm-project/vllm#67325, merged 2026-11-18 as `abb8194dc3`. It is not in v0.34.0. Recent vLLM releases came
  about two weeks apart. blis-substrate#88 tracks onboarding it.

**Engine upgrade.** One modelled commit serves both: a vLLM main commit at or after `abb8194dc3` has both models
(DC1, design §12.4). The alternative is Mistral-Large-4 with the v0.34.0 upgrade, and Inkling-2-Small with the next
release (v0.35, not yet cut).

**Table DC4. Neither model is expected to need new graph vocabulary, and both would run on GB200 with their main
kernels priced below measured until fitted. Mistral-Large-4's `config.json` is not yet read.**

| Piece | Inkling-2-Small | Mistral-Large-4 |
|---|---|---|
| Catalog entry | a branch of the existing Inkling handler. Its new nodes are of existing kinds: block attention residuals and MoE softcaps as elementwise nodes. Its DSpark drafter follows the catalog's other DSpark drafters | a new handler combining kinds the catalog has: DSA sparse attention (as GLM-5), and a layer that reads another layer's KV cache and reuses another layer's indexer (as DeepSeek-V4.1). To confirm from its gated `config.json` |
| New graph vocabulary | none expected | none expected, until the `config.json` is read |
| Model support (design §12.5) | likely needed. It ships its own kernels (relative-position FA4 attention, a custom TRT-LLM batched GEMM for its MoE, its own all-reduce), which `engines/vllm` must lower | probably small. Its KV sharing and sparse index groups are close to DeepSeek-V4.1's, still to check against `core/kv` |
| Coefficients on GB200 | NVFP4 and MXFP8 grouped MoE GEMMs have no entry on any Blackwell part. Until fitted, they are priced from a lower-ranked entry: transferred, roofline or assumed. Relative-position attention is priced as plain attention, an approximation | sparse-MLA attention has no GB200 entry (its 31 entries are all on H100 and H200), so it too is priced from a lower-ranked entry until fitted. The MLA decode floor on GB200 is assumed |
| Drafter acceptance | borrowed from another profile | borrowed from another profile, unless a measured Mistral-Large-4 profile exists |

If neither model brings a new kind of layer, as expected, the catalog entry and the engine pieces do not depend on
each other. Every kernel can be priced (VAL-2, design §9.2), so a new primitive family needs assumed entries on each
catalog chip before the model can run. AISimulate's GB200 collection is the likeliest fit data for these kernels.
Whether it covers these two kernel families is not yet checked. If no source covers them, they stay at a lower
rank, named on each point (§1.6).

**Answer to the team.** Report each configuration with a stated confidence. Neither model has measured runs on
GB200, so each configuration is a prediction with no held-out evidence, and its main costs use transferred or
assumed values until they are fitted. On GB200, BLIS predicts decode time per token about 1.35 times too high
until blis-substrate#140 and blis-vllm#272 land (§0.2).

## 0. Carried from M3.1

**Maintainer.** Whatever was planned for M3.1 and did not make the M3.1 release is handled in M3.2. Nothing planned
for M3.1 is dropped without a record: each issue was either closed by the M3.1 pull requests or is listed here.

M3.1's plan is section 3.1 of the release plan, with its issues in the plan's `m31_scope.tsv` (189 issues). Its seven pull requests merged on
2026-11-18 between 20:19 and 21:23 UTC: blis-substrate#361, blis-vllm#275, blis-sglang#126, llm-d-router#21,
inference-sim#2237, accuracy-dashboard#133 and blis-config-search#150. M3.1 was released as inference-sim v0.18.1
at 21:32 UTC. The status below is as of 2026-11-19 04:10 UTC.
Issue numbers of blis-substrate, blis-vllm and blis-sglang change when DC3 transfers the issues; this section and
`m31-carried.tsv` are re-mapped then, and the pin sequences behind several of the items go away.

**0.1 What the M3.1 review asked for, and where it stands.**
- *Finish after Schedule in SGLang*, which blocked blis-sglang#126 and inference-sim#2237: fixed in blis-sglang#150,
  and inference-sim pins the fixed engine (`03d72d6f`). Done.
- *Per-pool KV connector and offload* (blis-substrate#307): the code merged (blis-substrate#402, blis-vllm#302,
  inference-sim#2252), but #307 is still open. Close it, or say what remains. CPU-offload sweeps on P/D in
  blis-config-search (blis-config-search#94) are not done, and carry into M3.2.
- *Borrowed acceptance named on stderr* (inference-sim#2079): done in inference-sim#2250.
- *config-search review fixes* (the acceptance entry, part of #93; probe packaging; the demo re-run): done in
  blis-config-search#155.
- *A simulator refusal is a named not-scored point*: done in accuracy-dashboard#158 and blis-design#32.
- Also fixed in review: issue #2221 by inference-sim#2249 (pool chips refused without a node-pool bundle); #2218 by
  inference-sim#2246 (the P/D per-instance measured window); #2214 and #2220 by inference-sim#2251 (p2p transfer at
  unequal TP); #2219 by inference-sim#2247 (the router check); the measured Muse DSpark acceptance in the 21
  scenarios and the DeepSeek 1P1D scenario's flags, by inference-sim#2248.

**0.2 Moved to M3.2 by decision.**
- blis-sglang#141, SGLang's SchedulerRecvSkipper (draft, checks failing).
- GB200 decode cost: blis-vllm#272 (Muse Spark's fused-kernel launches, held back from M3.1) and blis-substrate#140
  (the 3.2 µs launch cost still used on GB200). Until both land, BLIS predicts GB200 decode time per token about
  1.35 times too high.
- blis-vllm#158: BLIS's KV pool for Muse Spark is 1.25 to 1.30 times the size vLLM logs at TP8, and 1.88 to 2.04
  times with DSpark, against a target within 5% of vLLM's.
- blis-substrate#369: the pre-registration and held-out verdict for the Blackwell launch fit.
- Smaller items: the `moe_backend` and `mm_encoder_tp` settings, rows whose record returns 404, the rows from
  frameworks BLIS does not model, the DeepSeek-V4 environment-variable bundle, and the "same kernels" wording in
  blis-substrate#294 and blis-vllm#298 (a wording fix, separate from what those pull requests closed).
- On the dashboard: the chip-split card, and SGLang rows on the public cards.
- Closed at the M3.1 merge, but worth a check: blis-substrate#125 (no engine pads a drafter's DP batch yet) and
  blis-substrate#116 (its GB200 value is still transferred; §0.6).

**0.3 Dropped by decision.** Accuracy figures for the internal experiments, raised in the accuracy-dashboard#133
review. Under §1.4 the internal experiments are training data, so they get no accuracy figure. How well BLIS
reproduces them is reported as a labelled training diagnostic (§4.3).

**0.4 The M3.1 plan issues still open.** Of the 189 issues, 39 are closed and 150 are open. All 150 carry into
M3.2, for closing or for work. [`m31-carried.tsv`](m31-carried.tsv) lists them, with each one's plan item and any note from the review. A
few are done in code and only need closing, such as inference-sim#2079 (fixed by inference-sim#2250) and
inference-sim#2214 (fixed by inference-sim#2251).

**Table 0.4. The 150 M3.1 plan issues still open, by plan item; SGLang end to end (C2) and data-parallel serving
(T1) are the largest groups.**

| M3.1 plan item | Open issues, carried into M3.2 | Count |
|---|---|---|
| P1 Release by commit | blis-substrate #193, #204, #340, #343, #345; inference-sim #2145, #2149, #2215 | 8 |
| P2 M3.0 review debt | blis-substrate #331, #332, #335, #337, #338 | 5 |
| H1 Pull requests deferred from M3.0 | inference-sim #1493, #1495, #2052, #2129 | 4 |
| B1 Correctness | accuracy-dashboard #100; blis-config-search #129, #133; blis-sglang #55, #91; blis-substrate #310; blis-vllm #214; inference-sim #2152, #2201, #2214 | 10 |
| A1 Launch and step cost per chip | blis-substrate #93, #114, #115, #121, #134, #136, #140, #152, #242; blis-vllm #72, #161, #191 | 12 |
| C1 Dashboard coverage | accuracy-dashboard #22, #58, #62, #63, #65, #79, #83, #87, #89, #90, #110, #111 | 12 |
| C2 SGLang end to end | blis-sglang #32, #38, #40, #44, #49, #56, #57, #61, #62, #63, #64, #65, #66, #67, #68, #70, #71, #73, #74, #75, #76, #77, #84, #94 | 24 |
| S1 Every capability sweepable | blis-config-search #93, #94, #125, #138 | 4 |
| R1 Command-line surface | inference-sim #2216 | 1 |
| A2 Time before the engine, and prefill | blis-substrate #75, #94; inference-sim #2094 | 3 |
| A3 KV capacity and memory | blis-substrate #73, #76, #132, #255, #281, #294; blis-vllm #73, #129, #158; inference-sim #1969 | 10 |
| C3 Closeness grades | accuracy-dashboard #53; blis-substrate #41, #43; inference-sim #2101, #2103 | 5 |
| C5 Catalog by points blocked | accuracy-dashboard #7; blis-substrate #91, #105, #106, #109, #126, #179, #188, #245, #258, #317 | 11 |
| A4 Collectives and MoE paths | blis-substrate #118, #123, #146, #150; blis-vllm #74, #75, #108 | 7 |
| A5 Speculative acceptance | accuracy-dashboard #59, #80; blis-substrate #144, #164; inference-sim #2079, #2115, #2125, #2136, #2141, #2142 | 10 |
| T1 Data-parallel serving and network structure | accuracy-dashboard #61, #64, #91; blis-substrate #48, #49, #50, #51, #153, #161, #346; blis-vllm #64; inference-sim #1988, #2126, #2146, #2164 | 15 |
| T2 KV tiers under P/D | blis-substrate #307; blis-vllm #47, #132, #146, #184, #190, #204; inference-sim #2202, #2203 | 9 |

In C2, SGLang speculation, attention data parallelism, expert parallelism and P/D (blis-sglang #64 to #71) stayed
refused in M3.1, as blis-sglang#126 states. A comment on blis-substrate#51 says what remains after switch groups.

**0.5 What becomes of blis-config-search#110.** The old #110 draft is superseded. The parts M2 and M3.1 already
supply (`draft_model`, acceptance recording, CPU and per-pool offload) are out of its scope. The remainder becomes
four workstreams in blis-config-search, each with its own pull request (to be assigned) and a test that says when
it is done:
- nested native speculative settings with recursive provenance (test: provenance round-trips);
- bounded sharding of exact search (test: sharded and unsharded results are equal as multisets);
- a durable per-attempt journal that keeps passed, refused and incomplete attempts (test: an interrupted search
  loses nothing);
- optional server-series diagnostics (test: collecting them does not change scoring).
Only the first depends on the engine's native speculative field list.

**0.6 Accuracy items from the M3.1 review, carried to M3.2.** None blocks a run. The figures are as reported in
the named issues.
- *The CPU tier ignores host memory the model holds* (inference-sim#1924). DeepSeek-V4.1's engram, a host-resident
  memory table, holds about 203 GB per node, but the CPU KV tier is sized as if all host memory were free. That
  overstates DeepSeek's CPU-offload capacity for P/D with CPU offload.
- *Muse DEP8 KV capacity* (blis-vllm#253). `muse-gb200-nvl-dep8-dspark.yaml` reports
  `kv_capacity_tokens_per_replica` of 500,977 tokens, against 8.09 million for TEP8, with a median TPOT of 39 ms at
  concurrency 4. It may be correct for 8 data-parallel ranks; check it against the engine's logged KV size. The
  config-search smoke test on the M3.1 head also found that DEP8 cannot fit a 1M-token context: it needs 72.5 GiB
  of KV per rank and has 40.1 GiB. This is unconfirmed.
- *CPU-load completion steps* (blis-vllm#305). BLIS reports a load completing N+3 engine steps after it starts.
  Add a test of the steps from load to admission against recorded vLLM runs. One recorded run: Muse-Spark-Open on
  16 GB200 GPUs, DSpark with 7 draft tokens, the uncapped AgentX workload. Its median TTFT at concurrency 64 is
  19.35 s with no CPU tier and 3.04 s with a 600 GiB tier. BLIS must reproduce that improvement.
- *The GB200 custom all-reduce is transferred from GB300* (blis-substrate#116, closed by blis-substrate#373).
  blis-substrate#373 fixed the lane: the price now follows the backend the engine resolved. The value did not
  change: 13.16 µs, `transferred_from: gb300`, against an estimate of about 7 µs for the custom lane. If a source
  named in §1 measures the GB200 4- and 8-rank custom all-reduce, use it. Otherwise the value stays transferred,
  with its source and rationale, and the points it prices name it (§1.6).

## 1. New data sources for calibration

1.1 **Maintainer.** Bring these data sources into BLIS for calibration:
- SGLang's nightly profiler traces, `github.com/sgl-project/ci-data` (step and host overhead, kernels);
- the vLLM CI perf API, `ci.vllm.ai/api/perf`, with the `vllm-project/perf-eval` recipes (current vLLM on H200
  and B200);
- SGLang's nightly job logs and `consolidated-metrics` artifacts (scheduler behaviour, resolved server
  arguments).

1.2 **Maintainer.** Licence is not a blocker, because BLIS queries the data and does not redistribute it.
**Proposal (accepted).** So none of it is committed to a public repository (design rule D6: only
redistributable artefacts are committed). Units are built from a pinned fetch at fit time, as the private internal
data is, and a public figure cites the source URL and the fetch date.

1.3 **Open.** Whether the rest of the inventory is also in M3.2's scope: Tritonbench nightlies (PyTorch's kernel
benchmarks), SGLang's AMD P/D nightly, the llm-d Prism archive, the vLLM blog's step tables, MoE tuning configs and
AgentX launch configs.

1.4 **Maintainer (2026-11-18).** The new data sets are used only for fitting and calibration. Accuracy on
accuracy-dashboard is reported only on the InferenceX and configiq units held out for it. Everything else is
training data for M3.2, used however serves accuracy best.
**Proposal**, to apply this:
- *Roles for new sources.* Each new source's ledger rule draws only training shares (fit, select and validate),
  with no held-out share. The split among the three is chosen per source.
- *What stays held out.* InferenceX and configiq keep their held and anchor shares unchanged. Accuracy figures
  come only from those.
- *Everything else is training data*: InferenceX's and configiq's training shares, the internal experiments, any
  source added under §1.3, and AISimulate's forward-pass set and the training shares of its sweeps. The sweeps also
  have a held share (20%; the ledger's rule draws fit 60, select 10, validate 10 and held 20), used only for
  operator-level checks of pre-registered changes; it never yields an
  accuracy figure.
- *No double use* (X8: no data point both fits and judges). A coefficient is never selected or graded on the units
  that fit it. Selection uses the select
  and validate shares, never the held-out shares. Roles are drawn per role key, so repeated measurements of one
  configuration never sit on both sides of that line.

1.5 **Proposal. Calibration acceptance gates, fixed before any fit** (VAL-6: the split and the success criteria
are committed first; design §12.3: a pre-registration is committed before any held-out data is read). Before any fitting reads these sources, fix:
- the baseline each fit must beat;
- the error metric, and the slices it must be reported on (at least engine, chip and workload);
- the minimum number of points per slice for a verdict (at least `min_points`, defined in §3B);
- the largest accuracy loss allowed on any other engine or chip;
- the held-out verdict, evaluated once, after selection;
- the rule for revising or reverting.
The maintainer still has to set the thresholds. Fitting waits until they are set.

1.6 **Maintainer (2026-11-18). No new GPU or cluster experiments, with no exceptions.** M3.2 fits, selects,
validates and evaluates only on data that already exists: the sources this section names. Where no source
measures a coefficient, the cost model uses the most trusted fallback entry (transferred, literature, vendor_spec,
roofline or assumed), written by its family's writer script, and names its method on every point it prices. It is replaced when data appears. A test that compares against measured runs uses runs already
recorded (for example blis-vllm#305). This includes DC4's GB200 kernels that no source measures.

## 2. Identifying each run's settings

2.1 **Maintainer.** For every run used, it must be possible to find its settings directly: the workload, the
cluster, the GPU type, the model and the engine settings. Getting these right is what makes the comparison like
for like. Identifying them is a standing step of the M3.2 calibration process.

2.2 **Proposal (accepted).** Follow the standing rule. Every value comes from the run's own records. A value no
record holds is a named substitution with its source, and lowers the grade. No value comes from a BLIS default.
Each source's scenario writer has a test that checks every field against the record it came from.

2.3 **Proposal (accepted).** Table 2.3 names, per source, the record that settles each setting
(`evidence/SETTINGS-PROVENANCE.md`).

**Table 2.3. Each setting of the three new sources has a named record. The gaps are in the cells: a few vLLM rows
are not pinned to a commit, vLLM's resolved settings must be rebuilt from the recipe and vLLM's defaults, and the
traces' job logs have expired.**

| Setting | vLLM CI perf API | SGLang nightly metrics and logs | SGLang traces |
|---|---|---|---|
| Engine commit | the row's `image` tag (a few rows are not pinned) | the run's `head_sha` / `commit_sha` | the trace's run id, then the Actions run's `head_sha` |
| GPU and count | the row's `device`; the recipe's `gpu` and `num_gpus` | the runner label (`8-gpu-h200`) | the trace's `deviceProperties`; the runner label |
| Model and precision | the row's `model` and `precision`; the recipe | the metrics' `model`; the log | the trace directory's name; the test definition at the commit |
| Parallelism | the recipe's `serve_args` (the row's `tp` is TP × DP) | the log's `server_args` dump | the test definition at the commit; `distributedInfo` |
| Engine settings | the recipe's `serve_args` plus vLLM's defaults at the commit (the server log is private) | the log's `server_args` (resolved) | the test definition at the commit (the logs have expired) |
| Workload | the recipe's `vllm_bench` block and `run_vllm_bench.sh` | `one_batch_server.py`'s arguments at the commit (one static batch, seed 42) | `bs` (batch size) and `il` (input length) in the file name, and the profiler's step settings |
| Metric definition | `vllm bench serve` means, medians and p99, in seconds, aggregated over 3 repetitions (the statistic is to confirm, §2.4) | `latency`, and `last_ttft` (the last request's, not a mean) | per-step spans, rank 0 only |
| Host and cluster | `lib/gpu_profiles.yaml` (environment, Docker or Kubernetes) | the runner definition | the runner definition |

2.4 **Proposal (accepted).** Confirm these before any fit: the statistic `aggregate_perf.py` takes over
repetitions; `vllm bench`'s seed and range ratio at each commit; and how a recipe's revision is matched to a row's
date when the recipe changed on that day.

## 3. Which engine the data improves

3.1 **Maintainer.** Use calibration to improve both SGLang and vLLM. Data that can improve only one engine,
because a coefficient is fitted only on the engine it predicts, is still used. Some coefficients are shared and
others are not.

3.2 **Proposal (accepted).** Kernel coefficients stay keyed by kernel implementation, so SGLang data fits vLLM's
value wherever both engines run the same implementation. Engine-path costs (host, scheduler, launch, CUDA-graph
replay) are keyed by the identity of the code that does the work, so each engine has its own value without an
engine name in the substrate (X2: no engine name or policy in the substrate). Today host overheads are scoped by
hardware and model only. Design v2.0.0 adopts the key (design §9.2, VAL-8); M3.2 builds it (Table DC, code identity
and host CPU).

## 3A. Maximise scorable coverage

**Maintainer.** Score every point that can be scored, especially for InferenceX. The dashboard nightly of 2026-11-18
(inference-sim v0.18.0, the M3.0 release) scored 238 of 20,364 InferenceX anchor units, all at G4. 7,182 of the
20,364 are on AMD parts, which are out of scope, leaving 13,182 in scope. In M3.1, 213 of configiq's
training and validation units could be simulated. `evidence/COVERAGE-FUNNEL.md` traces where the rest are lost.
The largest causes are policy (an age limit) and a ledger frozen at one dump; missing records block some older
runs.

**Proposal (accepted, 2026-11-18).** Older points count in the headline at their own grade, and are not split off.
The grade already says how closely a point's setup matches what BLIS ran, and a separate table would hide
coverage. The headline always shows its breakdown by grade, so the same-release figure is one slice away (§3B).

The rest of this section is proposal unless marked.

3A.1 **The ledger follows each source.** Every row InferenceX publishes is ingested once, not only the rows of
db-dump/2026-09-28 plus hand-pinned supplements (records added one by one after the dump). Rows that measure the
same unit join that unit; units that share a role key share a role. New rows are pinned by record id and content
SHA-256, as supplements are today, but the ingest tool adds them on a schedule instead of by hand. New units draw
their roles by the existing rule, so the partition does not change. On 2026-11-18 the API served 1,216 in-scope
rows dated after the dump that are not units at all; 1,133 of them are vLLM- or SGLang-family. Each new source of
§1 also joins the ledger continuously, with training shares only (§1.4).

3A.2 **Maintainer (2026-11-18). No age limit on scoring.** The 180-day age limit stops being a gate. Every anchor
unit whose inputs can be recovered is scored, at its grade. On the dashboard nightly of 2026-11-18, 11,555 in-scope
anchor units are older than the limit (measured before 2026-05-23; the 180 days include 2026-11-18). Removing the limit makes them eligible; it does not make them scorable when their
inputs are gone (§3A.8). A date range becomes a slice (§3B).

3A.3 **Recover inputs from durable records, and keep the ones that expire.**
- vLLM single-turn runs: the InferenceX API's `/server-log`. It returned logs for every dump-only record tested
  from 2026-02 to 2026-07, and none before 2026-02 (§3A.8).
- SGLang and P/D runs: the job log while GitHub keeps it, otherwise the recipe or script at the run's commit. The
  dashboard's pull already does this.
- Measurements the API no longer serves, because a newer measurement of the configuration superseded them: the
  dump. 949 in-scope anchor units inside the age limit are missing from the dashboard nightly for this reason alone.
- Inputs that expire (GitHub job logs and artifacts after a retention period of about 90 days; agentic exports):
  archived privately as they are pulled, and never committed publicly (design rule D6). A point then stays
  scorable after the source deletes them.
- A point whose inputs are gone is G5, with a reason that names the missing record.

3A.4 **Engine and table gaps, in order of the points they hold back** (dashboard nightly of 2026-11-18, which ran
M3.0's v0.18.0).
- SGLang-family: 173 in-scope anchor units inside the age limit were blocked because M3.0 had no SGLang field list, 96 of
  them by that alone. M3.1 publishes the list. There are 2,949 in-scope SGLang-family anchor units
  in all.
- Dynamo's router (NVIDIA's serving framework) has no entry in the router table: 254 anchor units inside the age
  limit.
- Settings no engine module models (`data_parallel_rpc_port`, NCCL and FlashInfer environment variables,
  `use_trtllm_attention`, `moe_backend` and others): each is modelled, proven inert or given an estimation rule, in
  order of the points it alone holds back.
- TRT-LLM stays refused: BLIS has no TRT-LLM engine.

3A.5 **Runs on other engine commits are scored.** A run on the modelled commit is the same build and can reach G1
or G2. A run on any other commit names its commit distance and is graded G3 or G4 (design §11.3, COV-6), for both
engines.

3A.6 **Report coverage as a funnel for InferenceX and configiq**, each release: the rows the source holds, units,
units in scope, units with recoverable inputs, units scored, and units scored by grade, with the top blockers by
the points they alone hold back. The new sources (§1.4) get a training-coverage count instead: rows held, units,
units with recoverable inputs, and units used in a fit. Each drop is a stated number.

3A.7 **configiq.** The maintainer has sent the configiq team questions, and is waiting for answers. Meanwhile their
repositories are read to recover each setting (§3C).

3A.8 **Expected effect.** The maintainer expects the shares to stay the same and the counts to rise. The role draw
does not change (Terms). The held-out units grow because the same shares apply to many more scorable points.
Table 3A.8 gives upper bounds from the dashboard nightly of 2026-11-18 and the ledger.

**Table 3A.8. Scored InferenceX anchor units could grow from 238 to about 2,800, or up to about 4,700; configiq's
held-out units could grow from none to between about 187 and about 630.**

| | Today | M3.2 ceiling | What opens it |
|---|---|---|---|
| InferenceX anchor units scored | 238 | about 2,800; up to about 4,700 | the list below |
| InferenceX held units | not on the dashboard | about 1.5 times the anchor units | the same sources; held units are 1.5 times anchor units both for new units (30% and 20%) and within the older held group (60% and 40%) |
| configiq held-out units (held and anchor) | none, until they are published (below) | about 187 if only forge-written H200 and B200 units are scored (half of 373, current revision, §3C.1); about 630 if all 1,257 H200 and B200 units are (pinned revision) | §3C's rule for each writer. The draw is per role key (328 keys), so the share is approximate |

The InferenceX anchor ceiling adds up as follows:
- the 238 scored today;
- 329 unscored anchor units inside the age limit that are not TRT-LLM;
- 1,143 vLLM-family and 863 SGLang-family anchor units from 2026-02 on that are older than the age limit or
  superseded;
- about 220 anchor units among the post-dump rows (20% of about 1,090 vLLM- and SGLang-family units);
- that gives about 2,800. Up to 1,913 more SGLang-family anchor units from before 2026-02 count if their recipes at
  the run's commit still resolve, for about 4,700.

TRT-LLM's 4,938 in-scope anchor units stay refused.

The ceilings assume every listed unit's inputs are recovered. The InferenceX API serves only the latest
measurement of each configuration. In M3.1, 213 of the 573 vLLM points in AISimulate's matched set had lost their
record (404); that 213 is not configiq's 213.

**Measured on 2026-11-18.** The InferenceX API's `/server-log` was queried for 33 vLLM single-turn records that
only the dump holds, three per month. Every record from 2025-09 to 2026-01 returned 404, and every record from
2026-02 to 2026-07 returned a log. On that sample, the 3,758 vLLM-family anchor units measured before 2026-02 are
expected to have no server log on the API. Whether the dump itself holds their logs is not yet checked; until then
they count toward no ceiling.
SGLang points take their launch command from the recipe at the run's commit, not from this endpoint, so the older
SGLang anchor units count as "up to" until that path is checked.

**Proposal.** Measure the count before planning: pull every anchor unit, checking only that its inputs can be
fetched, without simulating, and report the count. configiq's units are not yet in the published anchor and fit
lists on blis-substrate `main`, so its held-out set must be published before it can be scored.

3A.9 **Proposal. Treat the dump as frozen, and reconcile it with the live API.** InferenceX published a dump
weekly from April to September 2026, and none after `db-dump/2026-09-28`. The pinned dump is now a fixed source
whose runs are on ever older vLLM and SGLang releases, while every new run comes only from the API. The rule that
splits record ids between them (the dump owns ids up to the cutoff, supplements own the ids above it) does not
state that the dump is final. To apply:
- *Treat the dump as a frozen archive.* It is the only copy of history before 2026-09-28, including measurements
  the API has superseded and no longer serves, and it will not grow. All new coverage comes from §3A.1's automatic
  API supplements.
- *Give each benchmark run one `measured_date`, across the cutoff.* A benchmark run's date is the earliest date
  over all its records. Ingest already reads the dump and the API supplements together, so a run with early
  records in the dump and later ones on the API keeps one date, and its units keep one identity (blis-substrate
  `ledger/cmd/ledger/main.go` passes both to `inferencex.IngestWithSupplements`; the dashboard's pull takes the
  date from the ledger). §3A.1's automation must keep that: it must never ingest new API rows apart from the
  dump. A test should pin it, with a run whose records straddle the cutoff and whose units keep one date.
- *Grade old runs by their commit distance.* Dump runs on old releases carry §3A.5's commit distance. Under
  §1.4, their training shares feed calibration. Their anchor share counts in the headline at its grade (§3A, the
  maintainer's decision), and their held share in pre-registered evaluations. The same-release figure is a slice
  (§3B).
- *Show the split.* Keep each point's source (`dump` or `api`) and its commit distance, and have §3A.6's funnel
  and §3B's slices report what share of the held-out units comes from the dump and what share from the API. A
  headline dominated by old dump runs is then a stated number.
- *Never re-pull a dump row from the API.* The API and the dump can report the same row's numbers differently: the
  dashboard nightly already marks 5 units `row_differs_from_ledger`. The API also lacks the dump's superseded history. Keep
  the id split.

## 3B. Slice accuracy by any recorded attribute

**Maintainer.** As more sources come in, accuracy must be sliceable by all their data attributes. A version of this
exists today.

Today the dashboard nightly's summary breaks counts down by engine, engine release, chip and grade, and the dashboard filters
only on multi-node runs and on the estimate tier (whether a point's values were estimated), over a fixed grouping by model, hardware and framework.

**Proposal.** Every scored point carries its attributes, and the dashboard filters and groups by any of them, with
every aggregate recomputed from the points that remain (as `filter.ts` already does):
- source and role;
- model, precision, chip, node count, interconnect;
- engine, engine commit, and its commit distance;
- topology (TP, DP, EP, P/D pools), speculative method, offload and KV tiers, router;
- workload type, ISL and OSL, concurrency, arrival process, prefix sharing;
- measured date;
- grade, and each substitution named on the point.
Each slice shows its point count and coverage beside its accuracy, so a small slice cannot pass for a strong
result.

**Proposal (accepted; raised in team review). The rule for small slices.** `min_points` is 10. Today the dashboard
shows a bare "too few points" for any figure over fewer than 10 points, while the per-point table below it still
lists every measurement, so the two appear to disagree, and the label covers most fine slices. The rule:
- the point rows stay visible at every count;
- an aggregate accuracy figure is never shown below `min_points`, at any level, from the headline to a drilled-in
  slice, and an aggregate not shown is excluded from every verdict;
- in its place the dashboard shows the count (`n=3 · mean withheld`), and the per-point table states the rule;
- the threshold stays at 10, and a test pins the behaviour.
An earlier idea, to stop applying the rule in a drilled-in slice, is dropped: it let a small slice look like strong
evidence. Tracked in accuracy-dashboard#160.

## 3C. configiq: settings and closeness

Evidence: `evidence/CONFIGIQ-FINDINGS.md` (Red Hat's repositories, read on 2026-11-18; the parser's regular
expression and forge's `cpt.yaml` checked by hand). The configiq team's answers are still pending, and they
override anything inferred here.

Three things write configiq's rows: **forge** (`openshift-psap/forge`, Red Hat's open-source benchmark launcher),
manual imports, and **Model Furnace** (an earlier, private Red Hat launcher). The publisher keeps a filtered copy of
Red Hat's private results CSV.

**Correction to how BLIS reads blanks.** BLIS treated a blank engine column as "not recorded" unless the row matched
a forge preset. A blank means the flag was not passed only for rows forge wrote. The publisher extracts settings
from a free-text `runtime_args` field with a regular expression, which misses space-separated values and bare
flags. So a blank in a manually imported or Model Furnace row can hide a value the run set. A blank
`prefix_caching` never means "on".

All of §3C is proposal, pending the team's answers.

3C.1 **Classify each row by its writer.** The counts are on the current dataset revision, which has 1,710
whole-run units; the ledger's pinned revision has 1,702. Family A is forge's, recognised by a `/v1/...` request
type and prefix caching on: 779 units, 373 of them on H200 or B200. Family C is manual imports: 128 units. Family D
is Model Furnace and older manual imports: 803 units. No family B was found. The family decides how blanks are read.

3C.2 **Family A: fill every blank from forge's own records**, each named as the substitution it is:
- the CPT matrix (forge's per-model test matrix, `cpt.d/cpt.yaml`) and the presets at the commit in force on the
  run's date, matched on model, TP, KV dtype and request type;
- vLLM's defaults at that release and device, for flags forge never passes (`max_num_seqs`, chunked prefill,
  `max_num_batched_tokens`, precision);
- the run's frame from forge's history: a concurrent load profile, a measurement duration of 275 s from 2026-09-22,
  the warm-up and ramp-up then in force, the GuideLLM release, seed 42, `ignore_eos`, and streaming.
This replaces today's preset match, which misses `cpt.yaml`.

3C.3 **Family D: fill only what the public benchmark guide and Model Furnace's defaults support.** That is prefix
caching off, and a measurement duration of 450 s or 600 s, when `max_seq_len` is 8192 or 10000 and memory
utilisation is 0.92. These are estimated substitutions and lower the grade. Rows whose TP is 1 may have used data
parallelism, and stay unscored.

3C.4 **Check each filled frame against the data.** The measurement duration derived by Little's law from the
concurrency-1 row must agree with the frame used. Only successful requests are compared.

3C.5 **Model each configiq workload as it ran**: the multi-turn shapes (`benchconf`'s `interactive-chat`, with a
first prompt of about 4,000 tokens and 45 s between turns) and the prefix workloads.

3C.6 **Pin the dataset revision.** The dataset is not append-only: 444 rows were removed between two revisions.

3C.7 **Ask Red Hat**, beyond the questions the maintainer already sent (§3A.7), to:
- publish an allow-listed `runtime_args`, the image tag, the GuideLLM version, the cluster tag, the start and end
  times, DP and the turn index;
- fix the case mismatch that drops DP;
- publish more of the roughly 52 models their internal CSV holds.

## 4. Proposals not yet discussed, and items superseded

4.1 **Proposal.** Start archiving the sources that expire now, before M3.2 starts, so their history keeps growing
instead of rolling off: SGLang's job logs and metrics artifacts (kept about 90 days), and Tritonbench (90 days) and
SGLang's AMD P/D artifacts (30 days) if §1.3 brings them in. The plan lists this as a prerequisite.

4.2 *Superseded by §3A.5 and §1.4.* InferenceX and configiq runs on other releases are scored with a commit
distance (§3A.5). The new sources are fitted, never scored.

4.3 *Superseded by §1.4.* The new sources are not reported on accuracy-dashboard as accuracy. The dashboard may show
how well the fitted model reproduces them, as a training diagnostic labelled as such.

## 5. CI: editing a pull request's text must not change its merge state

5.1 **Maintainer (2026-11-18, revised 2026-11-19).** Editing a pull request's title or body never changes its merge
state. CI runs only when the pull request's code changes.
- No CI check reads a pull request's title or body. The text is maintainer practice, reviewed by people
  (design v2.0.0's rule that process is maintainer practice).
- Workflows trigger on `pull_request` events of type `opened`, `synchronize` and `reopened`, and on a change of
  base. An `edited` event triggers nothing.
- This supersedes the earlier idea of separate required checks that read the text.
