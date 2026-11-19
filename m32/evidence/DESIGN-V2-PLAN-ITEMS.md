# Implementation particulars from the design v2.0.0 audits

Design v2.0.0 states rules, not one upstream release's particulars. The audits of v2.0.0 found the particulars
below. The design now states the rule that covers each one. The M3.2 implementation supplies each particular,
mostly through each engine module's surface list and its generators (design §7.5), and the upgrade report
(design §12.4). Each item names the rule it serves. Table DC in `requirements.md` section DC builds them.

The tables group the items by component. In each table, the first column is the item and the second is the
design rule it serves.

## vLLM (`engines/vllm`)

Table 1. vLLM items.

| Item | Design rule |
|---|---|
| Lowering selects the per-device tuned fused-MoE configuration file that vLLM selects, and hashes it into the kernel's `CodeHash`. A run is G1 only when its tuned configuration is the one BLIS selected. | §9.2 kernel key; G1 (§11.3) |
| `gpu_memory_utilization` changed its default between commits. The diff generator reads defaults, constants and registry contents at any two commits, so that G3 compares a run's resolved defaults with the modelled commit's. | FID-14; G3 (§11.3) |
| Record the backport paths in the `Upstream` record: the model directories, the config parsers and the architecture registry. | §12.5; FID-14 |
| Use a faked-device CUDA platform class to obtain the platform's block-size preferences, instead of transcribing them. | FID-1 |
| Generate `code_paths.json`, the closure of engine-path code that each host, scheduler and graph cost depends on. | §9.2 code identity |
| Settle full-block and partial-block KV-event emission under each report mode from the block pool and coordinator source at the modelled commit, and record it in the surface list. The design no longer calls it inferred. | §7.5 |
| Under asynchronous scheduling a request first joins the step after the next. Record this particular in the engine's declared step boundary. | DEV-3 |

## SGLang (`engines/sglang`)

Table 2. SGLang items.

| Item | Design rule |
|---|---|
| The P/D allocation policy setting is `disaggregation_decode_allocation_policy`, with values `early` (the default) and `prefill_complete`. The port reproduces both, and the surface list records the setting and its default. | §6.4; SGL-3 |
| The radix-tree core defaults to the Rust implementation, selected by an environment variable. The oracle runs both cores. The Go port follows the default, a T2 differential case compares the two, and the surface list names their divergences. | FID-2; SGL-1 |
| The behaviours formerly tabled in the design move to the surface list: new-token ratio, maximum prefill tokens, retraction, output limits, maximum running requests under speculative decoding, and KV event hashing. | §7.5; SGL-3 |
| Generate `code_paths.json` for the engine-path closures. | §9.2 code identity |
| The compared field `new_token_ratio` is the admission look-ahead ratio in the design. The field name lives in the SGLang surface list and field list. | §7.5 |
| The radix cache (unified radix cache by default, with the Python and Rust tree cores) and the drafters (EAGLE3, DSpark, DFlash, vLLM's `draft_model`) are named only in the surface lists. | §7.5 |

## Substrate, catalog and simulator

Table 3. Substrate, catalog and simulator items.

| Item | Design rule |
|---|---|
| Generate each engine's `kernel_impls.json` as an engine-neutral copy under `substrate/registry/inputs/`, with a freshness check. Move the VAL-8 cross-check into a simulator-package test. | X7; VAL-8 |
| Add the all-language path-reference lint: no file under `substrate/` names a path under `engines/`. | X7 |
| Add `CodeID` to `HostPlan` and `GraphPolicy`. | §6.2; §9.2 |
| Add the `host_cpu` fact to node packaging (x86 hosts for H100 and H200, Grace for GB200). Scope engine-path coefficients by it. | SUB-3; §9.2 |
| Validate the GB200 (Blackwell) to Hopper transfer rules (VAL-5, leave one generation out) before use. Until then, a cross-generation transfer ranks as roofline. | §9.2; VAL-5 |
| Connector and backend names of the vLLM and SGLang KV trees live only in each engine module's surface list. The NIXL storage-plugin mapping (GDS, POSIX, object plugins) is recorded there at the modelled commit. | §7.3; §7.5 |
| Each engine module's surface list records, at its modelled commit, the per-engine behaviours the design states as kinds with examples: asynchronous scheduling depth, overlap scheduler, P/D allocation policy, KV-event granularity and report mode, and the memory budget formula. Class names in design §7.1 are examples only; the surface list is the authority. | §6.4; §7.1; §7.5 |
| The Transformers-backed fallback paths of vLLM and SGLang are surface-list items. Generate them, and list the models that run only through a fallback in the upgrade report. | §7.5; §12.4 |
| Record InferenceX's client multiples for `measurement_contaminated` (10 measured, 2 warm-up, 12 in all) as a fixed multiple in the ledger's source record. | §10.2 |

## A future engine (TensorRT-LLM)

These are the first cases for the native-code step of design §12.6.

Table 4. TensorRT-LLM items.

| Item | Design rule |
|---|---|
| The steady-clock read in the eviction policy is a time site. | FID-1 |
| The `getenv` read of the window-size shares in the KV-cache manager is an environment site. | FID-1 |
| The capacity scheduler exists twice, as a C++ binding and in Python. The oracle runs both. | FID-2 |
| The pool allocation sites. | FID-1 |
| An instrumented build for branch coverage. | FID-4 |
| The engine-plan path has no meta-tensor dispatch mode. Name the per-layer launch and shape dump, or the instrumented native run, that the design accepts for it. | FID-7; FID-11 |
