# BLIS M3.2 requirements

These are the working requirements for M3.2, the release after M3.1, captured with the maintainer from
2026-11-18. They are not yet a plan, and more will be added. The design they build on is
[design v3.0.0](https://inference-sim.github.io/blis-design/v3.0.0/blis-target-design.html).

**Labels.** Each item carries one label:
- **Decided**: stated, decided or accepted by the maintainer.
- **Proposal**: open to correction.
- **Open**: not yet decided. An Open item names its owner and what decides it.

Section DC lists what M3.2 builds for design v3.0.0. It comes first because the maintainer asked that design
changes be the first requirement. It cites later sections.

**Evidence.** The notes in `evidence/`, next to this file, back the figures:
- what vLLM, SGLang and PyTorch publish as performance data (`INVENTORY.md`);
- where each new source records its run settings (`SETTINGS-PROVENANCE.md`);
- why so few InferenceX and configiq points are scored (`COVERAGE-FUNNEL.md`);
- how configiq rows are produced (`CONFIGIQ-FINDINGS.md`);
- what the two models a team requested need on GB200 (`NEW-MODELS-GB200.md`).

Figures are as of 2026-11-18, except the M3.1 status in §0, which is as of 2026-11-19 04:10 UTC. Every repository
named here is under `github.com/inference-sim/` unless another owner is shown.

## Terms

**Repositories.** Design v3.0.0 has one simulator repository and the router fork. M3.2 builds that layout (DC3).
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

**Design rules, sections and terms.** IDs such as X7, SUB-15, LIF-5, COV-6, T-M1 or D6 name rules of design v3.0.0.
The letters group them: X across components, SUB substrate, LIF versions and releases, COV accuracy coverage, VAL
coefficients, D the ledger, T a trigger's test. A design section is written "design §n.m" and links to the design.
A bare § number is this file's own section (§0 to §4, §3A to §3C); the design changes are DC1 to DC3 and the team
request is DC4, without a §. The design's glossary, [Appendix B](https://inference-sim.github.io/blis-design/v3.0.0/blis-target-design.html#appB),
defines these terms, which keep its sense here: anchor, commit distance, drafter, engine module, engine upgrade,
funnel, graph handler, graph vocabulary, headline, held-out unit, lowering, model backport (written "backport"),
model support, named substitution (an **estimated substitution** is one whose value comes from a stated rule rather
than a record), onboarding a model, oracle, primitive family, role key, router table, slice, training data and
upgrade report. The design's term "lane" has a wider sense than this file needs, so the dashboard's per-engine groups
are called groups here.

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
- **Role**: each unit has one of fit, select, validate, held or anchor, drawn once per role key by a
  seeded rule (design §10.2). Fit units fit coefficients, select units choose between fits, validate units check a
  fit. **Held-out** units are held (one evaluation per pre-registration) and anchor (the **headline**, the
  dashboard's accuracy figure). **Training data** is every fit, select or validate unit and all
  data from a source with no held or anchor role.
- New InferenceX and configiq units draw 30% fit, 10% select, 10% validate, 30% held and 20% anchor. Older units
  were first split into a fit group and a held group; each stays in its group, and the ledger's rules split each
  group into roles (fit and select; held and anchor).

**Grades.** G1 (exact) to G5 (not scored), as design
[§11.3](https://inference-sim.github.io/blis-design/v3.0.0/blis-target-design.html#s11-3) defines them. G1 and G2
need the run's own engine commit; G3 and G4 are other commits, by commit distance.

**Coefficients.**
- **Coefficient methods** are ranked in design §9.2: measured, calibrated, transferred, literature, vendor_spec,
  roofline, assumed. A lookup uses the most trusted entry the registry has, and records its method. A **fallback
  entry** is one whose method is transferred, literature, vendor_spec, roofline or assumed; it is used where no
  measured or calibrated entry exists, and every point it prices names its method.
- **TRT-LLM**: NVIDIA's TensorRT-LLM serving engine, which BLIS does not model. **vLLM-family**, **SGLang-family** and
  **TRT-LLM-family** group InferenceX's frameworks by the engine underneath, as `evidence/COVERAGE-FUNNEL.md` Table F2
  lists them (for example, the vLLM family includes Dynamo and llm-d deployments of vLLM).
- **P/D**: prefill/decode disaggregation, where separate GPU pools run the prefill and decode phases.
- **Abbreviations**: TP, DP and EP are tensor, data and expert parallelism. TTFT is time to first token and TPOT
  time per output token. ISL and OSL are input and output lengths in tokens.
- **Age limit**: the dashboard's rule, today, that scores only runs measured in the last 180 days (§3A.2).
- **Speculative decoding** uses a small drafter model to propose tokens. **DSpark** is one drafting method.
  **Acceptance** is the share of drafted tokens the target model keeps.

## DC. Design changes (DC1 to DC3) and a team request (DC4)

**Status.** M3.2 implements [design v3.0.0](https://inference-sim.github.io/blis-design/v3.0.0/blis-target-design.html).
The design states the rules. DC1 to DC3 are **Decided**: the design adopts them, and this section states each once.
Table DC lists what M3.2 builds. Rule IDs and sections are those of v3.0.0. The lowering work of DC2, planned
for M4, is part of M3.2.

**Why.** Changes crossed repositories in sequence: the per-pool offload fix took blis-substrate#402, blis-vllm#302
and inference-sim#2252, with full CI at each. And the new data (§1) is pinned to engine commits, not releases, which
BLIS could not model.

### The decisions

**DC1. An engine module models one upstream commit, not only a release.**
A run on the modelled commit is the same build and can be graded G1 or G2. A run on any other commit names its
commit distance and is graded G3 or G4. A model that lands upstream between upgrades is added as a model backport,
which carries model code only. An engine upgrade produces an upgrade report of the models the new commit supports.
In the design: design §7.1, §11.3, §12.4 and §12.5, and Table 1 in design §2.2; LIF-5, LIF-6, COV-6, T-E1 to T-E6,
FID-14.

**DC2. Lowering lives only in engine modules.**
The catalog's graph deriver writes checkpoint facts and nothing else. The `onboard --plan` command is removed:
simulating the requested scenario and the upgrade report answer the same questions. The substrate has no rule
layer, so `contracts/rules/` is removed. A model that needs no model support and no new primitive family is
onboarded by one catalog pull request. In the design: SUB-15, SUB-12, T-M1, T-M2 and design §12.1.

**DC3. blis-substrate, blis-vllm and blis-sglang become directories of inference-sim.**
They are packages of inference-sim's one Go module (`substrate/`, `engines/vllm`, `engines/sglang`). The router fork,
accuracy-dashboard, blis-config-search and blis-design stay separate. The router fork owns the hosting contract and
its conformance suite, so it depends on no BLIS module and inference-sim imports it without a cycle. In the design: design §2.1, §2.2, §3.2, §3.4, §5.3 and §14.4 (Table 1, the layout, checks by directory, the router
fork and release branches, in that order); X7, X11, SUB-1, SUB-13, RTR-3. X10 (bottom-up merge) is retired.

**DC4** is a team request, not a design change; it follows the build list below.

### What M3.2 builds for DC1 to DC3

**Table DC. M3.2 implements the adopted design; each row is work, not design. A group's header row names its
Table W workstream, and the last column names the design rule a row serves. Order: the migration first, because the
other groups are easier in one repository.**

| Group | What M3.2 builds | Rule |
|---|---|---|
| **Migration (DC3), in this order** | Table W rows 1 and 2 | |
| Sizing | Size the migration from the actual workflows, checks and open issues before it starts. It is not sized yet. Output: a list of workflows, checks and open issues per repository, and the pull-request sequence for the migration and the two groups that follow it (Table W rows 2, 3 and 5) | |
| Hosting contract | Move `contracts/embed` and `contracts/conformance/embedtest` (about 2,300 lines of Go; 12 commits of history touch them) into the router fork as new files in `blisembed/`. New files cost none of the fork's patch budget (`hack/hosting-lint/budget.txt`); the edits to its `go.mod` and `go.sum` do. The fork's import test (`TestImportsOnlySubstrateContracts`) then forbids every `github.com/inference-sim/` package. Update the checks that name blis-substrate as the contract's home: `hack/embed-apidiff.sh` and its test, `hack/fork-policy/main.go` and `.github/workflows/hosting-lint.yml` in the fork; `contracts/architecture_test.go` and the SUB-1 API-diff check in blis-substrate. The conformance suite runs in the fork's CI. inference-sim imports the contract through its one `replace`, under llm-d's module path (`github.com/llm-d/llm-d-router/blisembed`) | X7, X11, SUB-1, RTR-3 |
| Subtree merge | Merge blis-substrate, blis-vllm and blis-sglang into inference-sim as `substrate/`, `engines/vllm` and `engines/sglang`, with a subtree merge that keeps their history. Every moved directory becomes a package of the one Go module | SUB-13 |
| Issues | Transfer the open issues of the three repositories and map the old numbers to the new. Re-map §0 and `m31-carried.tsv` when they land | |
| Checks | Replace the repository boundaries with an import-graph lint over directories (`go list`, required in CI) and the path-reference lint of X7 (no file under `substrate/` names a path under `engines/`). Consolidate each repository's merge rules, checks and workflows. Make heavy CI path-filtered, so a change runs only the jobs of the directories it touches. Restate each invariant's "Runs in" by directory in `substrate/contracts/invariants`. Add the module-size check | X2, X7, SUB-13, design §3.4 |
| Releases | Per-engine release branches become release branches of inference-sim, which already cuts `release-v0.18`. Re-point the pins of accuracy-dashboard and blis-config-search | design §14.4, X11 |
| Retire | Archive blis-substrate, blis-vllm and blis-sglang with a pointer to inference-sim, once the issues are transferred | |
| **Lowering (DC2)** | Table W row 5 | |
| Deriver | Move all vLLM lowering out of the catalog's graph deriver into `engines/vllm`; the deriver writes checkpoint facts only, and its `--check` and rederivation test stay | SUB-15 |
| Rules layer | Remove `contracts/rules/` and move model values into graph fields; each engine module's refusal is the engine layer of validation | SUB-12 |
| **Any commit (DC1), all engines** | Table W row 3 | |
| Generators | Make `gen_surface.py`, `gen_kernel_impls.py` and `gen_fields.py` work at any commit. Today `gen_surface.py` refuses a checkout at another commit, `gen_kernel_impls.py` needs one `kernels/<tag>/attention.json` per release, and `gen_fields.py` holds release-specific paths. Lock the oracle environment to the commit | X9, FID-2, T-E3 |
| Upgrade report | Generate the report of design §12.4 (surface diff, field demand, source diff, and for each model the catalog entry, model support and missing coefficients). Every new surface entry gets a status. The dashboard uses the same diff generator to grade a run. Include the Transformers-backed fallback paths of vLLM and SGLang as surface-list items, and list the models that run only through them | X9, design §12.4, design §11.3 |
| Commit identity | Name commits in `stack.json` and in the scenario refusal; accept an on-demand commit in the release watcher; grade by commit distance in the dashboard | LIF-6, SIM-3, COV-6 |
| Backports | List backported commits in the Upstream record and check that every catalog model that does not use one has identical plans and traces with and without it | FID-14, T-M5 |
| **vLLM (`engines/vllm`)** | Table W row 4 | |
| Tuned MoE configuration | Lowering selects the per-device fused-MoE configuration file that vLLM selects, and hashes it into the kernel's `CodeHash`. A run is G1 only when its tuned configuration is the one BLIS selected | design §9.2, G1 |
| Defaults at two commits | `gpu_memory_utilization` changed its default between commits. The diff generator reads defaults, constants and registry contents at any two commits, so that G3 compares a run's resolved defaults with the modelled commit's | FID-14, G3 |
| Platform preferences | Use a faked-device CUDA platform class for the block-size preferences, instead of transcribing them | FID-1 |
| KV events | Settle full-block and partial-block KV-event emission under each report mode from the block pool and coordinator source at the modelled commit, and record it in the surface list | design §7.5 |
| Step boundary | Record the step N+2 behaviour under asynchronous scheduling in the declared step boundary | DEV-3 |
| Backport paths | Record in the Upstream record the model directories, config parsers and architecture registry that a backport may change | design §12.5, FID-14 |
| **SGLang (`engines/sglang`)** | Table W row 4 | |
| P/D allocation | The setting is `disaggregation_decode_allocation_policy`, `early` (the default) or `prefill_complete`. The port reproduces both, and the surface list records the setting and its default | SGL-3, design §6.4 |
| Radix-tree core | The Rust core is the default. The oracle runs both cores, the Go port follows the default, a T2 differential case compares them, and the surface list names their divergences | FID-2, SGL-1 |
| Surface list | Record the admission look-ahead ratio (`new_token_ratio`), maximum prefill tokens, retraction, output limits, maximum running requests under speculative decoding, KV-event hashing, the radix cache and drafter lists, and the NIXL storage-plugin mapping at the modelled commit. Every engine module's surface list also records, at its modelled commit, asynchronous scheduling depth, overlap scheduler, P/D allocation policy, KV-event granularity and report mode, and the memory budget formula; the surface list, not the class names in design §7.1, is the authority | SGL-3, design §7.5 |
| **Substrate and simulator** | Table W row 6 (code identity and host CPU) and row 7 (the rest) | |
| Code identity | Generate `code_paths.json` (the closure of engine-path code that each host, scheduler and graph cost depends on) for both engines, and add `CodeID` to `HostPlan` and `GraphPolicy`. This is the key for engine-path coefficients (§3.2). On an engine upgrade, each engine-path identity that changed gets a transferred entry from its previous identity until it is refitted (design §9.2, §12.4) | design §9.2, VAL-8 |
| Host CPU | Add the `host_cpu` fact to node packaging (x86 hosts for H100 and H200, Grace for GB200) and scope engine-path coefficients by it | SUB-3, design §9.2 |
| Kernel lists | Generate each engine's `kernel_impls.json` as an engine-neutral copy under `substrate/registry/inputs/` with a freshness check, and move the VAL-8 cross-check into a simulator-package test. Connector and backend names of the vLLM and SGLang KV trees live only in each engine's surface list, with the NIXL storage plugins (GDS, POSIX and object) | X7, VAL-8, design §7.5 |
| Cross-generation transfer | Validate the GB200 (Blackwell) to Hopper transfer rules (leave one generation out) before use. Until then a cross-generation transfer ranks as roofline | VAL-5, design §9.2 |
| Ledger multiples | Record InferenceX's client multiples (10 measured, 2 warm-up, 12 in all) for `measurement_contaminated` in the ledger's source record | design §10.2 |
| **Held-out gate (design v3.0.0)** | Table W rows 25 and 26 | |
| Whole-run gate | Build the whole-run landing gate in accuracy-dashboard. A candidate job with no secret builds the candidate and runs the pinned harness on every unit not on the published fit or anchor lists. The secret-holding gate job computes roles, scores held units only and returns aggregates over at least `min_points` role keys, with VAL-6's statistics: a non-inferiority margin, a one-sided 95% BCa interval from 10,000 resamples by role key, Holm over lanes and criteria, and the merging of small lanes. It gives one evaluation per pre-registration and counts each against the partition version's budget. It reports on the pull request, runs nightly, and runs before each release against the previous release and the best published release | [VAL-6](https://inference-sim.github.io/blis-design/v3.0.0/blis-target-design.html#s9-4), D7, design §12.3, design §13.5 |
| Gate as the path | Every M3.2 change that moves accuracy goes through the whole-run gate: each refit, each coefficient change and each engine upgrade. The calibration of the new sources (row 18) lands only through it | VAL-6, T-A1, T-A2 |
| Operator-level evidence | Remove the operator-level held-out gate from the ledger workflow. The error job keeps reporting each method's error on validate units nightly, as method error, never as accuracy; it informs review and never decides a landing | VAL-5, VAL-11, design §13.5 |
| AISimulate roles | Write a new partition version that changes only AISimulate's cut-points to training roles (fit 0 to 69, select 70 to 84, validate 85 to 99) and keeps the partition secret. No InferenceX or configiq unit changes role, and no secret is published | D4, D7, D9 |
| **Simplifications (design v2.1.0 to v2.4.0)** | Table W rows 8 and 22 | |
| Simulator commands | Remove the `ledger`, `invariants` and `compose` commands from inference-sim, with their tests and docs pages, and the `blis invariants` mention in the README. Nothing calls them: the dashboard reads the ledger from the release checkout, and the substrate's own tool renders the invariant blocks | COV-2, X29, DEV-7 |
| Ledger embedding | Stop embedding `catalog/ledger/published/` in the simulator's data; the loader ignores everything under `catalog/ledger/` | design §3.3, design §10.2 |
| Dashboard nightly | Delete the stale "TEMPORARY until `blis ledger --list anchor`" comment in `api-nightly.yml`. It already reads the anchor list from the pinned checkout | COV-2 |
| Gated-config nightly | Delete the substrate's `nightly-fetch-configs.yml` and its entries in `.github/check-runs.yaml`; remove the `config-fetch` environment and its `HF_TOKEN` secret. Keep `fetch_pinned_configs.py` and `derive_graph.py --check --fetched`, which a maintainer runs. Add the gated-model step to the catalog README and a checkbox to the pull-request template, outside the generated block | X12 |
| InferenceX unit regeneration | Delete the Postgres regeneration step ("Regenerate the InferenceX units from the pinned dump") from the `gate-nightly` job of the substrate's `ledger.yml`. Keep the D2 join and the configiq regeneration. Add the local regeneration step (restore the dump, export, `ledger check-generated`) to the ledger README and a checkbox to the pull-request template, for a change to the dump pin or the ingest tool | D4 |
| Process checks | Retire the checks that design v2 made maintainer practice. Delete `shared-nightly.yml` in the substrate (cited issues, quarantine list, private names in issue text) and the `schedule` trigger of the `blis` workflow in inference-sim, blis-substrate, blis-vllm, blis-sglang and blis-config-search. Delete the `tags.lock` check. From `shared-pr-checks.yml`, delete the pull-request body fetch and the description, commit-policy, review-thread, cited-issue and quarantine steps; signing and sign-off are set in branch protection. Keep the workflow lint, version literals, documentation references, licence and notice files, the generated copies and the selected-version lint. The VLM-3 field-list check stops reading issues | X28, X25, X14, X20, X24, LIF-1, LIF-3, VLM-3, design §4.2 |
| Report role | Remove `RoleReport` from the ledger (`roles.go` and the published-list loops in `assign.go` and the ledger command), delete `catalog/ledger/published/report.yaml`, and update their tests. No unit holds the role, so no unit moves | design §10.2, D4, D7 |
| Stale citations | Update the citations of closed issues that the nightly reports: 1 in inference-sim, 4 in blis-sglang, 4 in blis-config-search and 25 in blis-substrate. Where the gap is fixed, remove the comment; where it is not, cite an open issue that tracks it. No issue is reopened only to clear a check | X28 |
| **A future engine (TensorRT-LLM)** | The first cases for the native-code step of design §12.6. Not built in M3.2; the sites are recorded in the surface list, with Table W row 4: the eviction policy's steady-clock read, the `getenv` of the window-size shares, the native and Python capacity schedulers (the oracle runs both), the pool allocation sites, an instrumented build for branch coverage, and, because the engine-plan path has no meta-tensor dispatch mode, a per-layer launch and shape dump or an instrumented native run for it | FID-1, FID-2, FID-4, FID-7, FID-11 |
### DC4. Support requested by a team: Mistral-Large-4 and Inkling-2-Small on GB200

**Decided (2026-11-19).** This is an M3.2 requirement, not a design change and not a patch release of M3.1.

**Request.** A GB200 configuration for both models on 16 GPUs, the capacity of Muse Spark (a model already in the
catalog; its open checkpoint is Muse-Spark-Open), for the team to use and verify. DC4 is done when each scenario
simulates on GB200 with every coefficient's method named, and the team's verification run is recorded.

**Facts** (checked 2026-11-18; `evidence/NEW-MODELS-GB200.md`).
- **Mistral-Large-4.** `MistralLarge4ForCausalLM`, with a DSpark drafter. It is in vLLM v0.34.0, released
  2026-11-16, and on vLLM main. It is not in v0.33.0, which blis-vllm models. Its Hugging Face repository is gated.
- **Inkling-2-Small.** `Inkling2ForConditionalGeneration`, 594B parameters. It is only on vLLM main, added by
  vllm-project/vllm#67325, merged 2026-11-18 as `abb8194dc3`. It is not in v0.34.0. Recent vLLM releases came
  about two weeks apart. blis-substrate#88 tracks onboarding it.

**Engine upgrade. Open.** Owner: the maintainer. Which upgrade: (a) one vLLM main commit at or after `abb8194dc3`,
which has both models (DC1, design §12.4), or (b) v0.34.0 for Mistral-Large-4 and the next release (v0.35, not yet
cut) for Inkling-2-Small. Recommendation: (a), because one upgrade serves both and the upgrade report lists both
models. The maintainer decides from that report and records the choice in an issue (design §12.4). Table W row 9
starts when the choice is recorded, and row 3 names the commit.

**Table DC4. Neither model is expected to need new graph vocabulary, and both would run on GB200 with their main
kernels priced by a fallback entry until fitted. Mistral-Large-4's `config.json` is not yet read. The detail is in
`evidence/NEW-MODELS-GB200.md`.**

| Piece | Inkling-2-Small | Mistral-Large-4 |
|---|---|---|
| Catalog entry | a branch of the existing Inkling handler; its new nodes are of existing kinds | a new handler combining kinds the catalog has (DSA sparse attention as GLM-5, shared KV and indexer as DeepSeek-V4.1); to confirm from its gated `config.json` |
| New graph vocabulary | none expected | none expected, until the `config.json` is read |
| Model support (design §12.5) | likely needed: it ships its own kernels, which `engines/vllm` must lower | probably small: its KV sharing and sparse index groups are close to DeepSeek-V4.1's, still to check against `core/kv` |
| Coefficients on GB200 | NVFP4 and MXFP8 grouped MoE GEMMs have no entry on any Blackwell part; relative-position attention is priced as plain attention, an approximation | sparse-MLA attention has no GB200 entry (its 31 entries are all on H100 and H200); the MLA decode floor on GB200 is assumed |
| Drafter acceptance | borrowed from another profile | borrowed from another profile, unless a measured Mistral-Large-4 profile exists |

If neither model brings a new kind of layer, the catalog entry and the engine pieces can proceed in parallel. A new
primitive family needs assumed entries on each catalog chip (VAL-2). AISimulate's GB200 collection is the likeliest
fit data for these kernels; whether it covers these two kernel families is not checked (the first task of Table W
row 9). If no source covers them, they stay on a fallback entry, named on each point (§1.6).

**Answer to the team.** Report each configuration as a simulator scenario file per model, with each main kernel's
coefficient method named. Confidence is low if any main kernel is transferred, roofline or assumed. Neither model has
measured runs on GB200, so each configuration is a prediction with no held-out evidence, and its main costs use
transferred or assumed values until they are fitted. The GB200 decode error of §0.2 applies.

## 0. Carried from M3.1

**Decided.** Whatever was planned for M3.1 and did not make the M3.1 release is handled in M3.2. Nothing planned
for M3.1 is dropped without a record: each issue was either closed by the M3.1 pull requests or is listed here.

M3.1's plan is section 3.1 of the release plan; its 189 issues are in the plan's `m31_scope.tsv`. The status below
is as of 2026-11-19 04:10 UTC. Issue numbers of blis-substrate, blis-vllm and blis-sglang change when DC3 transfers
the issues; this section and `m31-carried.tsv` are re-mapped then, and the pin sequences behind several of the
items go away.

**0.1 Still open from the M3.1 review.** blis-substrate#307 (per-pool KV connector and offload): the code merged
(blis-substrate#402, blis-vllm#302, inference-sim#2252). Close #307, or say what remains. CPU-offload sweeps on
P/D (blis-config-search#94) carry into M3.2. The other review items were fixed in M3.1 (Table M).

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
- Closed at the M3.1 merge, but worth a check: blis-substrate#125 (no engine pads a drafter's DP batch yet).

**0.3 Dropped by decision.** Accuracy figures for the internal experiments, raised in the accuracy-dashboard#133
review. Under §1.4 the internal experiments are training data, so they get no accuracy figure. How well BLIS
reproduces them is reported as a labelled training diagnostic (§1.4).

**0.4 The M3.1 plan issues still open.** Of the 189 issues, 39 are closed and 150 are open. All 150 carry into
M3.2, for closing or for work. [`m31-carried.tsv`](m31-carried.tsv) lists them, with each one's plan item and any
note from the review. A few are done in code and only need closing, such as inference-sim#2079 (fixed by
inference-sim#2250) and inference-sim#2214 (fixed by inference-sim#2251).

**Table 0.4. The 150 M3.1 plan issues still open, by plan item; SGLang end to end (C2) and data-parallel serving
(T1) are the largest groups. `m31-carried.tsv` lists the issues.**

| Plan item | Open | Plan item | Open |
|---|---|---|---|
| P1 Release by commit | 8 | A3 KV capacity and memory | 10 |
| P2 M3.0 review debt | 5 | C3 Closeness grades | 5 |
| H1 Pull requests deferred from M3.0 | 4 | C5 Catalog by points blocked | 11 |
| B1 Correctness | 10 | A4 Collectives and MoE paths | 7 |
| A1 Launch and step cost per chip | 12 | A5 Speculative acceptance | 10 |
| C1 Dashboard coverage | 12 | T1 Data-parallel serving and network structure | 15 |
| C2 SGLang end to end | 24 | T2 KV tiers under P/D | 9 |
| S1 Every capability sweepable | 4 | R1 Command-line surface | 1 |
| A2 Time before the engine, and prefill | 3 | | |

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
- *Muse DEP8 KV capacity* (blis-vllm#253). `muse-gb200-nvl-dep8-dspark.yaml` (Muse Spark, DEP8: 8 data-parallel ranks with expert parallelism for the experts; TEP8 shards attention 8-way and the experts with expert parallelism) reports
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

1.1 **Decided.** Bring these data sources into BLIS for calibration:
- SGLang's nightly profiler traces, `github.com/sgl-project/ci-data` (step and host overhead, kernels);
- the vLLM CI perf API, `ci.vllm.ai/api/perf`, with the `vllm-project/perf-eval` recipes (current vLLM on H200
  and B200);
- SGLang's nightly job logs and `consolidated-metrics` artifacts (scheduler behaviour, resolved server
  arguments).

1.2 **Decided.** Licence is not a blocker, because BLIS queries the data and does not redistribute it. So none of
it is committed to a public repository (design rule D6: only redistributable artefacts are committed). Units are
built from a pinned fetch at fit time, as the private internal data is, and a public figure cites the source URL and
the fetch date.

1.3 **Open.** Whether the rest of the inventory is also in M3.2's scope: Tritonbench nightlies (PyTorch's kernel
benchmarks), SGLang's AMD P/D nightly, the llm-d Prism archive, the vLLM blog's step tables, MoE tuning configs and
AgentX launch configs. Owner: the maintainer, who decides before Table W row 13 ingests the new sources. Default if no
decision: out of M3.2.

1.4 **Decided (2026-11-18).** The new data sets are used only for fitting and calibration. Accuracy on
accuracy-dashboard is reported only on the InferenceX and configiq units held out for it. Everything else is
training data for M3.2, used however serves accuracy best. Applied as follows:
- *Roles for new sources.* Each new source's ledger rule draws only training shares (design D9); the split among
  fit, select and validate is chosen per source. A new source is never reported as accuracy; the dashboard may show
  how well the fitted model reproduces it, as a training diagnostic labelled as such.
- *What stays held out.* InferenceX and configiq keep their held and anchor shares unchanged. Accuracy figures
  come only from those.
- *Everything else is training data* (design D9): the training shares of InferenceX and configiq, the internal
  experiments, any source added under §1.3, and all of AISimulate, its sweeps and its forward-pass set. AISimulate's
  sweeps lose their held share (20% of files today) to training roles (Table DC "AISimulate roles").
- *The landing gate is whole-run.* Changes land on held InferenceX and configiq units only, through the whole-run gate
  (design VAL-6, §13.5). A worse lane fails the change; a maintainer may land it only after recording the regression as a defect in another
  term (VAL-11). Operator-level method error on validate units is reported nightly and never decides a landing.
- *No double use* (X8). A coefficient is never selected or graded on the units that fit it, and selection uses the
  select and validate shares only.

1.5 **Decided (rule); Open (thresholds).** Calibration acceptance gates are fixed before any fit (VAL-6: the split
and the success criteria are committed first; design §12.3: a pre-registration is committed before any held-out data
is read). Before any fitting reads these sources, fix:
- the baseline each fit must beat;
- the error metric, and the slices it must be reported on (at least engine, chip and workload);
- the minimum number of role keys per slice for a verdict (`min_points`, design COV-13);
- the largest accuracy loss allowed on any other engine or chip;
- the held-out verdict, evaluated once, after selection;
- the rule for revising or reverting.
The thresholds are **Open**. Owner: the maintainer, who sets them in a pull request merged before any fit reads the
new sources (Table W row 18). No fit starts before then.

1.6 **Decided (2026-11-18). No new GPU or cluster experiments, with no exceptions.** M3.2 fits, selects,
validates and evaluates only on data that already exists: the sources this section names. Where no source
measures a coefficient, the cost model uses the most trusted fallback entry, written by its family's writer script,
and names its method on every point it prices. It is replaced when data appears. A test that compares against
measured runs uses runs already recorded (for example blis-vllm#305). This includes DC4's GB200 kernels that no
source measures.

## 2. Identifying each run's settings

2.1 **Decided.** For every run used, it must be possible to find its settings directly: the workload, the
cluster, the GPU type, the model and the engine settings. Getting these right is what makes the comparison like
for like. Identifying them is a standing step of the M3.2 calibration process.

2.2 **Decided.** Follow the standing rule. Every value comes from the run's own records. A value no
record holds is a named substitution with its source, and lowers the grade. No value comes from a BLIS default.
Each source's scenario writer has a test that checks every field against the record it came from (Table W row 14).

2.3 **Decided.** Table 2.3 names, per source, the record that settles each setting
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

2.4 **Decided.** Confirm these before any fit (Table W row 14): the statistic `aggregate_perf.py` takes over
repetitions; `vllm bench`'s seed and range ratio at each commit; and how a recipe's revision is matched to a row's
date when the recipe changed on that day.

## 3. Which engine the data improves

3.1 **Decided.** Use calibration to improve both SGLang and vLLM. Data that can improve only one engine,
because a coefficient is fitted only on the engine it predicts, is still used. Some coefficients are shared and
others are not.

3.2 **Decided.** Kernel coefficients stay keyed by kernel implementation, so SGLang data fits vLLM's
value wherever both engines run the same implementation. Engine-path costs (host, scheduler, launch, CUDA-graph
replay) are keyed by the identity of the code that does the work, so each engine has its own value without an
engine name in the substrate (X2: no engine name or policy in the substrate). Today host overheads are scoped by
hardware and model only; M3.2 builds the key (design §9.2, VAL-8; Table DC, code identity and host CPU).

## 3A. Maximise scorable coverage

**Decided.** Score every point that can be scored, especially for InferenceX. The dashboard nightly of 2026-11-18
(inference-sim v0.18.0) scored 238 of 13,182 in-scope InferenceX anchor units, all at G4 (`evidence/COVERAGE-FUNNEL.md`
Table F1 gives the funnel). The largest causes of loss are an age limit and a ledger frozen at one dump; missing
records block some older runs.

**Decided (2026-11-18).** Older points count in the headline at their own grade (design COV-2); the same-release
figure is a slice.

3A.1 **Proposal. The ledger follows each source.** Every row InferenceX publishes is ingested once, not only the
rows of the dump plus hand-pinned supplements. Rows that measure the same unit join it. New rows are pinned by record
id and content SHA-256 (design D3), added on a schedule by the ingest tool, and draw their roles by the existing rule.
On 2026-11-18 the API served 1,216 in-scope rows dated after the dump that are not units at all; 1,133 of them are
vLLM- or SGLang-family. Each new source of §1 also joins the ledger continuously, with training shares only (§1.4).

3A.2 **Decided (2026-11-18). No age limit on scoring** (design COV-2). Every anchor unit whose inputs can be recovered
is scored, at its grade. Removing the limit makes the 11,555 older in-scope anchor units eligible (Table F1), not
scorable when their inputs are gone (§3A.8). A date range is a slice.

3A.3 **Proposal. Recover inputs as design §11.6 orders the records** (server log from the source's API; job log while
kept, otherwise the recipe at the run's commit; a private archive; never committed, D6). M3.2 adds:
- vLLM single-turn runs use `/server-log`; it returned logs for every dump-only record tested from 2026-02 to
  2026-07 and none before (Table F2 note);
- 949 in-scope anchor units inside the age limit are missing from the dashboard nightly because the API no longer
  serves their superseded measurement; the dump supplies them;
- inputs that expire (GitHub job logs and artifacts, about 90 days; SGLang's job logs and metrics artifacts; agentic
  exports) are archived privately as they are pulled, starting now, before M3.2 starts, so their history keeps
  growing instead of rolling off (Table W row 11). Tritonbench (90 days) and SGLang's AMD P/D artifacts (30 days)
  join the archive if §1.3 brings them in.

A point whose inputs are gone is G5, with a reason that names the missing record.

3A.4 **Proposal. Engine and table gaps, in order of the points they hold back** (dashboard nightly of 2026-11-18, which ran
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

3A.5 **Decided.** Runs on other engine commits are scored, for both engines, by commit distance (design COV-6, DC1).

3A.6 **Decided.** Report coverage as design §11.6 states, for InferenceX and configiq, and the training funnel for
the new sources (§1.4). Every drop is a stated number.

3A.7 **configiq.** The maintainer has sent the configiq team questions, and is waiting for answers. Meanwhile their
repositories are read to recover each setting (§3C).

3A.8 **Proposal. Expected effect.** The maintainer expects the shares to stay the same and the counts to rise. The
role draw does not change (Terms). The held-out units grow because the same shares apply to many more scorable
points. Table 3A.8 gives upper bounds from the dashboard nightly of 2026-11-18 and the ledger.

**Table 3A.8. Scored InferenceX anchor units could grow from 238 to about 2,800, or up to about 4,700; configiq's
held-out units could grow from none to between about 187 and about 630.**

| | Today | M3.2 ceiling | What opens it |
|---|---|---|---|
| InferenceX anchor units scored | 238 | about 2,800; up to about 4,700 | the list below |
| InferenceX held units | not on the dashboard | about 1.5 times the anchor units | the same sources; held units are 1.5 times anchor units both for new units (30% and 20%) and within the older held group (60% and 40%) |
| configiq held-out units (held and anchor) | none, until they are published (below) | about 187 if only forge-written H200 and B200 units are scored (half of 373, current revision, §3C.1); about 630 if all 1,257 H200 and B200 units are (pinned revision) | §3C's rule for each writer; the points are provisional (below). The draw is per role key (328 keys), so the share is approximate |

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
record (404).

The 33-record `/server-log` test is in `evidence/COVERAGE-FUNNEL.md` (Table F2 note). On that sample the 3,758
vLLM-family units before 2026-02 have no server log on the API, and count toward no ceiling until the dump is
checked. Older SGLang units count as "up to" until the recipe path is checked.

**Provisional configiq points.** A configiq point whose blanks are filled from forge's records, or by preset match,
is provisional (design COV-7). Its grade is capped at G3 with the reason, it is shown in its own band and kept out of
the headline, and it is regraded when the source publishes the missing values. It is still a held-out unit, so the
configiq counts above include it with that cap.

**Proposal.** Measure the count before planning: pull every anchor unit, checking only that its inputs can be
fetched, without simulating, and report the count (Table W row 12). configiq's units are not yet in the published
anchor and fit lists on blis-substrate `main`, so its held-out set must be published before it can be scored.

3A.9 **Decided. The dump is a frozen archive and the API is the live feed.** Design D3 states the rule: the dump
owns record ids up to the cutoff, the feed owns the ids above it, a row is never pulled again from the other side,
and a run whose records straddle the cutoff keeps one `measured_date`. M3.2 adds:
- the scheduled supplement job of §3A.1 ingests API rows together with the dump, never apart from it;
- D3's test: a run whose records straddle the cutoff, whose units keep one date;
- each point records its source revision (`dump` or `api`; an attribute in design COV-13), and the funnel and the
  slices report the share of held-out units from each.

The API and the dump can give different numbers for one row (the dashboard nightly marks 5 units
`row_differs_from_ledger`), which is why the id split stays.

## 3B. Slice accuracy by any recorded attribute

**Decided.** As more sources come in, accuracy must be sliceable by every recorded attribute. Design COV-13 states the
rule: the attribute list, the point count, role-key count and coverage beside each figure, and `min_points` of 10
**role keys** (not points), below which no aggregate is shown at any level. M3.2 builds it in accuracy-dashboard
(accuracy-dashboard#160; Table W row 19).

Today the dashboard nightly's summary breaks counts down by engine, engine release, chip and grade, and the dashboard
filters only on multi-node runs and on the estimate tier (whether a point's values were estimated), over a fixed
grouping by model, hardware and framework. It shows a bare "too few points" for any figure over fewer than 10 points,
while the per-point table still lists every measurement. The test is COV-13's: ten points from two role keys render no
aggregate, and the point rows still render.

## 3C. configiq: settings and closeness

Evidence: `evidence/CONFIGIQ-FINDINGS.md` (Red Hat's repositories, read on 2026-11-18; the parser's regular
expression and forge's `cpt.yaml` checked by hand). The configiq team's answers are still pending, and they
override anything inferred here.

Three things write configiq's rows: **forge** (`openshift-psap/forge`, Red Hat's open-source benchmark launcher),
manual imports, and an earlier private launcher. The publisher keeps a filtered copy of
Red Hat's private results CSV.

**Correction to how BLIS reads blanks.** BLIS treated a blank engine column as "not recorded" unless the row matched
a forge preset. A blank means the flag was not passed only for rows forge wrote. The publisher extracts settings
from a free-text `runtime_args` field with a regular expression, which misses space-separated values and bare
flags. So a blank in a manually imported or earlier-launcher row can hide a value the run set. A blank
`prefix_caching` never means "on".

The rules 3C.1 to 3C.7 are **Proposal**, pending the team's answers. The correction above is a finding from the code, checked by hand.

3C.1 **Proposal. Classify each row by its writer.** The counts are on the current dataset revision, which has 1,710
whole-run units; the ledger's pinned revision has 1,702. Family A is forge's, recognised by a `/v1/...` request
type and prefix caching on: 779 units, 373 of them on H200 or B200. Family C is manual imports: 128 units. Family D
is the earlier launcher and older manual imports: 803 units. No family B was found. The family decides how blanks are read.

3C.2 **Proposal. Family A: fill every blank from forge's own records**, each named as the substitution it is:
- the CPT matrix (forge's per-model test matrix, `cpt.d/cpt.yaml`) and the presets at the commit in force on the
  run's date, matched on model, TP, KV dtype and request type;
- vLLM's defaults at that release and device, for flags forge never passes (`max_num_seqs`, chunked prefill,
  `max_num_batched_tokens`, precision);
- the run's frame from forge's history: a concurrent load profile, a measurement duration of 275 s from 2026-09-22,
  the warm-up and ramp-up then in force, the GuideLLM release, seed 42, `ignore_eos`, and streaming.
This replaces today's preset match, which misses `cpt.yaml`. The points are provisional (design COV-7; §3A.8).

3C.3 **Proposal. Family D: fill only what the public benchmark guide and the earlier launcher's defaults support.** That is prefix
caching off, and a measurement duration of 450 s or 600 s, when `max_seq_len` is 8192 or 10000 and memory
utilisation is 0.92. These are estimated substitutions and lower the grade. Rows whose TP is 1 may have used data
parallelism, and stay unscored.

3C.4 **Proposal. Check each filled frame against the data.** The measurement duration derived by Little's law from the
concurrency-1 row must agree with the frame used. Only successful requests are compared (the 8000/800 rows have many errored requests).

3C.5 **Proposal. Model each configiq workload as it ran**: the multi-turn shapes (`benchconf`'s `interactive-chat`, with a
first prompt of about 4,000 tokens and 45 s between turns) and the prefix workloads.

3C.6 **Proposal. Pin the dataset revision.** The dataset is not append-only: 444 rows were removed between two
revisions. Treat the 63 duplicated units as possibly from different clusters.

3C.7 **Proposal. Ask Red Hat**, beyond the questions the maintainer already sent (§3A.7), to:
- publish an allow-listed `runtime_args`, the image tag, the GuideLLM version, the cluster tag, the start and end
  times, DP and the turn index;
- fix the case mismatch that drops DP;
- publish more of the roughly 52 models their internal CSV holds.

## 4. CI: editing a pull request's text must not change its merge state

4.1 **Decided (2026-11-18, revised 2026-11-19).** Editing a pull request's title or body never changes its merge
state, and no CI check reads that text (design process rule). Workflows trigger on `pull_request` events of type
`opened`, `synchronize` and `reopened`, and on a change of base. An `edited` event triggers nothing (Table W row 22).

4.2 **Decided (2026-11-19).** CI checks product correctness only. The process checks that design v2 made maintainer
practice are retired, and no check reads an issue (design v2.3.0, X28 and VLM-3; Table DC "Process checks" and
"Stale citations", Table W row 22).
