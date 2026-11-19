# M3.2 Table W row 1: sizing the migration (DC3)

Scope: what moves, what checks it, and the pull-request sequence for rows 2, 3, 5 and 27. Read-only
measurement on 2026-11-19; nothing in any repository was changed. Row 1 depends on nothing; rows 27 then 2
depend on it.

Revisions measured (all are the heads of `main`, except the fork, whose product branch is `llm-d-r`):

| Repository | Head | The pin `stack.json` names | Pin is on `main` |
| --- | --- | --- | --- |
| inference-sim | `fe4228406` | | |
| blis-substrate | `9149031c6` | `b6748ca9d757` | yes |
| blis-vllm | `2348505f2` | `af87ac53acaf` | yes |
| blis-sglang | `d7c6e70aa` | `03d72d6fc3bf` | yes |
| llm-d-router fork | `ba3ad1688` (`llm-d-r`) | `601ff6e9d37d` | not checked |

Method limits: GitHub counts are from the API on 2026-11-19. The inference-sim clone here is shallow, so its
commit count comes from the API. The API returns rulesets only: classic branch protection is not readable with
this token, so "no required checks" below means "no ruleset rule".

## 1. Per repository: workflows, checks, open issues

| | inference-sim | blis-substrate | blis-vllm | blis-sglang | router fork (`llm-d-r`) |
| --- | --- | --- | --- | --- | --- |
| Workflow files | 15 | 14 | 7 | 5 | 31 |
| Jobs in `ci.yml` | 15 | 14 | 18 | 8 | none (`ci-*.yaml`, upstream's) |
| Required checks (ruleset on `main`) | 7 | 3 | 0 | 0 | 0 |
| Open issues | 118 | 137 | 94 | 53 | 0 |
| Open pull requests | 58 | 52 | 44 | 2 | 1 |
| Of the open issues, `M3.1` label | 33 | 59 | 18 | 26 | n/a |
| Carried to a row (`carried.tsv`, state not re-checked) | 27 | 54 | 17 | 26 | 0 |
| Commits (merge commits) | 669 (n/m) | 837 (276) | 1117 (250) | 300 (87) | upstream history |
| Tracked files / size | 1724 / 16 MB | 1051 / 45 MB | 2505 / 45 MB | 585 / 165 MB | n/m |
| Go module `go` line | 1.27.2 | **1.24** | 1.27.2 | 1.27.2 | n/m |
| Tags | 57 | 5 | 5 | 1 | n/m |
| Release branches | `release-v0.17`, `release-v0.18` | none | `release-v0.32.0` | none | n/a |

n/m = not measured. The fork's other 29 workflows are upstream's; the two BLIS-written ones are
`fork-policy.yml` and `hosting-lint.yml` (the others were not audited one by one).

### 1.1 Workflows by repository (what each does, trigger)

| Repository | Workflows |
| --- | --- |
| inference-sim | `ci.yml` (PR + push main; path-filtered by `scripts/ci-changes.sh`, aggregate job `required`), `gofmt.yml`, `golden-change.yml`, `private-names.yml`, `blis.yml` (calls the substrate's shared checks; PR + nightly cron), `ci-retarget.yml` (re-dispatch CI on a base change), `release.yml` (tag `v*`, Docker image), and the agent workflows `archon`, `claude`, `pr-review`, `deliver-{implement,verify,correct,stall-sweep,guards-selftest}` |
| blis-substrate | `ci.yml` (jobs `go`, `lint`, `contracts*`, `kernel*`, `catalog`, `registry`, `ledger`, `mutants`, `required`), `ci-light.yml` (docs-only path), `blis.yml`, `ledger.yml` + `ledger-candidate.yml`, `rederive.yml`, `acceptance-refresh.yml`, `nightly.yml`, `nightly-fetch-configs.yml`, `private-names.yml`, `rerun-ci.yml`, and three reusable `workflow_call` files: `shared-pr-checks.yml`, `shared-nightly.yml`, `rerun-on-runner-shutdown.yml` |
| blis-vllm | `ci.yml` (18 jobs: go-build/test/race/bench, `oracle-*` tiers, `packs-against-vllm`, `metrics-manifest`, `goldens-reviewed`), `ci-light.yml`, `blis.yml`, `mutation.yml`, `oracle-traces.yml`, `recorded-logs.yml`, `private-names.yml` |
| blis-sglang | `ci.yml` (8 jobs: `go`, `lint`, `oracle-*`, `treecore-diff`, `goldens-reviewed`, `fields`), `ci-light.yml`, `blis.yml`, `mutation.yml`, `private-names.yml` |
| fork | `fork-policy.yml` (jobs `history`, `commits`, `landed`; PRs to `llm-d-r` and `m3/**`), `hosting-lint.yml` (jobs `hosting`, `conformance`, `api-diff`, plugin audit), plus upstream's `ci-*`, `pr-*`, `issue-*`, release and stale workflows |

Required checks today: inference-sim's ruleset lists seven names (`build`, `lint` and five matrix-named
`test (<leg>, <packages>, <timeout>)` contexts); its `ci.yml` also has an aggregate job `required` that the
ruleset does not list. blis-substrate requires `required`, `pr / blis checks` and `scan`. blis-substrate keeps a
ledger of 89 checks and the check run that proves each (`.github/check-runs.yaml`, enforced by
`go test ./tools/release`); the release bot reads it. The three engine-side repositories and the fork have no
ruleset requirement, so their checks are advisory on merge.

### 1.2 Open issues: notable ones for the migration

| Issue | Why it matters here | Row |
| --- | --- | --- |
| blis-substrate#193 Engine repositories install Go from go.mod, not from `contracts/toolchain` | disappears with one module | 2 |
| blis-substrate#340 blis-sglang must re-pin to the merged substrate commit | moot once merged | 2 |
| blis-substrate#337 patch budget headroom is one line (449 of 450) | stale: measured 404 of 450 today; close or update at row 2 | 2 |
| blis-substrate#204 Remove `Scenario.EngineVersion` (a contract-change review set) | needs the SUB-1 accept-break id; ids change on transfer | 3 |
| blis-substrate#343, #345 router release workflows fail on every BLIS tag; remove `tags.lock` | the fork's release path and the tag-immutability file | 22 |
| inference-sim#2215 hosting lint accepts an unrelated Park before Wait | touches the fork's `hack/hosting-lint` | 2 |
| inference-sim#2214 p2p tier with unequal TP transfers via `cpu_dram` | listed "fixed by #2251; confirm and close" | 24 |
| blis-vllm#214, blis-sglang#55, #91 | engine behaviour issues; carry to rows 15 and 4 | 15, 4 |

Cross-repo facts for the transfer: GitHub transfers issues, not pull requests. The three repositories hold
**98 open pull requests** (52 + 44 + 2) that a maintainer must merge, close or re-open in inference-sim before
archiving. Issue numbers change (inference-sim is at #2262), so these must be re-mapped on transfer:
`m32/m31-carried.tsv` (97 of the 150 carried issues are in the three repositories),
`.github/contract-review-set` in blis-substrate (it names `blis-substrate#58`), the accept-break ids in
`hack/embed-apidiff-test.sh` (`#42`), and every `INV-*` or code comment that cites `blis-substrate#N`.
Labels and milestones transfer only where the destination has the same names.

## 2. The hosting contract's home (checks that name blis-substrate)

The contract is `contracts/embed` (1 non-test package) and `contracts/conformance/embedtest`: 3,353 lines of Go
with tests (the plan's "about 2,300" counts non-test files). Both import only the standard library, and
`embedtest` imports `embed`. So the move is a pure copy with an import rewrite; nothing else moves with them.

### 2.1 Checks in the fork

| File | What names blis-substrate | Change needed when the contract is `blisembed/` |
| --- | --- | --- |
| `hack/embed-apidiff.sh` | `contract()` (lines ~150-162) reads `go.mod` for a `blis-substrate` require and maps it to `./contracts/embed` (or `blis-schemas` to `./embed`); `contract` mode compares the package between the version the last `-blis` tag pinned and the version `go.mod` pins now; `fork` mode rewrites an old tag's `pkg/embed` imports onto HEAD's module | add a third case: the contract in this module (`blisembed`). `contract` mode compares `blisembed` at the tag against HEAD in-tree (no module download); `fork` mode maps the tag's `contracts/embed` imports to `blisembed`. The first release after the move has a tag that pins substrate, so the script's "contract moved between modules" path is the one to extend, not a new concept |
| `hack/embed-apidiff-test.sh` | cases 1-4 build fake tag and HEAD module pairs named `SUBSTRATE=github.com/inference-sim/blis-substrate`; the accept-break cases name `inference-sim/blis-substrate#42` | add a case "tag pins substrate, HEAD has it in-tree"; keep cases 1-4 as the history of how a prior move was handled |
| `hack/fork-policy/main.go` | `substrateModule` const; the `toolchain` check runs `go list -m` / `go mod download` for the substrate module and requires the go line to be no higher than `contracts/toolchain` | with the require dropped, `go list -m` fails. Needs a fork-local source of the toolchain line (a file in the fork, or the `substrate/contracts/toolchain` of inference-sim fetched at a pin). This is a design decision for row 2: the fork must not import inference-sim |
| `hack/fork-policy/deferral.go` (+ test `TestReadDeferralFromPinnedSubstrate`) | `deferralPath` read from the pinned substrate; returns "none" when absent. The current substrate head has `.github/modlint-deferral.yaml`, not the `x20-deferral.yaml` the fork reads, so the deferral is already effectively off on the pinned version (to confirm at the pin) | copy the deferral file into the fork, or delete the deferral logic and the X20 text if the deferral has ended |
| `.github/workflows/hosting-lint.yml` | step "Go toolchain is contracts/toolchain of the pinned substrate"; job `conformance` runs `pkg/embed` `TestConformance` against substrate's `embedtest` and `TestImportsOnlySubstrateContracts`; `api-diff` runs the two scripts above | the conformance step runs against `./blisembed/embedtest`; rename the X7 test (below); toolchain step follows the decision above |
| `pkg/embed/*.go` and `cmd`, `hack` | 29 import lines (21 of `.../contracts/embed` as `contract`, 8 of `.../embedtest`) | rewrite to `github.com/llm-d/llm-d-router/blisembed` and `.../blisembed/embedtest`; one `sed` |
| `pkg/embed/imports_test.go` | `TestImportsOnlySubstrateContracts` allows `blis-substrate/contracts/*` | per the requirements it then forbids every `github.com/inference-sim/` package; rename to `TestImportsNoInferenceSimPackage` and update the `hosting-lint.yml` `-run` pattern, `x.yaml` X7 and `rtr.yaml` RTR-3 citations |

### 2.2 Checks in blis-substrate

| File | What changes |
| --- | --- |
| `contracts/architecture_test.go` | `TestEmbedImportsOnlyTheStandardLibrary` (lines ~134-150) loops over `./embed` and `./conformance/embedtest`; delete, and restate its rule in the fork as a test over `blisembed` (the rule protects the fork: "a dependency here becomes a dependency of every router that implements it") |
| SUB-1 API-diff: `tools/prcheck/apidiff.go`, `prcheck contracts-apidiff`, job `contracts` in `ci.yml` | it lists every importable package under `contracts/`, so `embed` and `embedtest` drop out of the diff automatically once deleted; **continuity** of RTR-3 is then the fork's `embed-apidiff.sh contract` alone. First diff after the move: substrate's last tag still contains `contracts/embed`, so `contracts-apidiff` reports a removed package against that tag unless the accept-break path (`-accept-break owner/repo#n`, named in `.github/contract-review-set`) is used for that one PR |
| `contracts/invariants/rtr.yaml` (RTR-3 text and `test:` line), `x.yaml` (X7, ~l. 906: "repositories use only the router contract in `contracts/embed`") | restate: the contract lives in the fork as `blisembed`; `test:` fields are checked by a registry test, so a stale `test:` fails CI |
| `.golangci.yml` | comment lists `embedtest` among the contracts packages with exemptions; remove the entry |
| `.github/check-runs.yaml` | the ledger must have exactly one entry per `ci` check in the registry (`go test ./tools/release`): removing a test requires removing its entry in the same PR |
| `.github/contract-review-set` | holds `inference-sim/blis-substrate#58`; a contract change that removes `embed` is itself a contract-change review set (SUB-1), so this PR needs its own id or the accept-break |

### 2.3 Edits to the fork's `go.mod` and `go.sum`, and their patch-budget cost

The budget file is `hack/hosting-lint/budget.txt`: `max_changed_upstream_lines = 450`, base `b9393d1a9f1d` (the
upstream release); new files cost nothing; `go.mod` and `go.sum` are shared with upstream, so every added or
deleted line counts. Measured with `go run ./hack/hosting-lint -budget`:

| Quantity | Now | After the move (measured in a scratch copy: contract copied to `blisembed/`, imports rewritten, `go mod tidy`) |
| --- | --- | --- |
| Budget used | 404 of 450 in 42 upstream files | 401 of 450 (404 less the 3 lines; computed from the measured diff, the budget tool's total was not captured on the copy) |
| `go.mod` vs upstream base | +2 / -1 (the substrate `require`; `golang.org/x/tools v0.50.0` moves from indirect to direct) | +1 / -1 (x/tools only) |
| `go.sum` vs upstream base | +18 | +16 |

So the move costs no budget: new files (`blisembed/`, `blisembed/embedtest/`) are free and dropping the
substrate require returns 3 lines. The remaining 18 lines are x/tools (apidiff and `hosting-lint` use it), not
the contract. Headroom is 49 lines before and after. `hack/fork-policy` still shells out to
`go list -m` for the substrate module, which `go mod tidy` does not see; it fails at run time, not in tidy.
`hosting-lint.yml` runs `go mod tidy -diff`, so the go.mod/go.sum edit must come from a real `tidy`.

## 3. What `compat/` pulls in (row 27)

`go list -deps ./vllmengine` in blis-vllm (head `2348505f2`) shows vllmengine imports exactly seven `compat`
packages, plus the whole blis-vllm `rules/` tree (`rules`, `engineconfig`, `pack`, `v0_29`, `v0_31`, `v0_32`,
`v0_33`) and `internal/upstream`. Non-test lines (tests in brackets):

| Package | Lines | Imports (within blis-vllm) | vllmengine imports it |
| --- | --- | --- | --- |
| `compat/kernelmodel` | 5,628 (8,853) | engine, lowering, quantization, vllmsettings, `rules`, `rules/{engineconfig,pack,v0_33}` | yes |
| `compat/engine` | 5,747 (2,517) | internal/util, tokenid | yes |
| `compat/lowering` | 2,331 (1,393) | vllmsettings | yes |
| `compat/quantization` | 284 (172) | none | yes |
| `compat/vllmsettings` | 266 (250) | `rules/engineconfig` | yes |
| `compat/tokenid` | 13 (0) | none | yes |
| `compat/internal/util` | 7 (19) | none | yes |
| `rules/` tree | 7,614 (12,773) | | yes (through the above and directly) |
| `compat/build` | 2,950 (3,462) | engine, kernelmodel, kvtransfer, `rules/engineconfig` | **no** |
| `compat/kv` | 4,175 (7,217) | engine, util, kvkey, kvtransfer, prefix | **no** |
| `compat/contract` | 1,547 (767) | dplb, engine, kv | **no** |
| `compat/lora` | 628 (716) | engine | **no** |
| `compat/kvtransfer`, `kvkey`, `prefix`, `dplb`, `nixl` | 979 / 148 / 227 / 138 / 142 | small | **no** |

`core/` (25,123 non-test lines) already has its own `kv`, `lora`, `sched`, `placement`, `lower`, `metrics`,
`connector`, `engine`, `vllm`; `vllmengine` is 1,083 lines.

**Finding that the plan's row 27 does not state.** inference-sim imports the *unused-by-vllmengine* `compat`
packages itself: 104 Go files import `blis-vllm/compat/*` (38 in `sim/cluster`, 26 in `cmd`, 18 in `sim/llmd`,
5 in `tools/harness`, plus `internal/stack`, `scripts/kernel/*`), 12 of them non-test. Import counts:
`compat/engine` 69, `kernelmodel` 31, `build` 13, `lora` 8, `kv` 6, `contract` 3, `prefix` 2, `dplb` 1,
`tokenid` 1. `cmd/engine_build.go` is "the one place inference-sim builds blis-vllm": it blank-imports
`compat/kv` and `compat/lora`, which register the KV store and adapter registry that `sim.NewEngine` builds,
and calls `compat/build` for offload, engine-knob and routing-override resolution. So "delete `compat/`" cannot
land in blis-vllm alone: it needs a paired inference-sim change at the new pin, and a decision per package
listed "no" above (port to `core/`, or replace by the `vllmengine` path). The "done when" (`go list -deps ./...`
lists neither `compat/` nor `rules/`) is about blis-vllm; inference-sim's own `go list -deps ./...` would still
list `compat/*` until its imports change.

Also affected: blis-vllm's `kerneltests/` (9 files import `compat`), `tools/harness`, root tests
(`architecture_test.go`, `imports_test.go`, `fields_test.go`), `surface.json`, `fields.json` and
`kernel_impls.json` (generated; their generators name the paths).

## 4. Module size and history (SUB-13)

| Source | Tracked size | Largest directory |
| --- | --- | --- |
| inference-sim | 16 MB | `sim` 5 MB |
| blis-substrate | 45 MB | `catalog` 35 MB, `registry` 5.5 MB |
| blis-vllm | 45 MB | `core` 34 MB |
| blis-sglang | 165 MB | `core/metrics/testdata/golden-metrics` **135.5 MB** (24 trace files) |
| Merged | **about 271 MB** | |

SUB-13 (`TestModuleZipIsUnder100MB`, which builds the zip with `modzip` and sums uncompressed sizes) says
under 100 MB; Go's hard limit is 500 MB. The merged module is about 2.7 times the SUB-13 limit, and one
directory of blis-sglang is the cause. Options for row 2 (decision needed before the third merge): keep the
traces out of the module (regenerate from the oracle, or fetch by sha256 at test time), compress them, or restate
SUB-13 for the merged module below Go's limit with the reason. The check must be restated in inference-sim
(requirements: "Add the module-size check"); `go.mod` of the merged module cannot have a nested `go.mod`
(`TestNoNestedModule`, SUB-13); the three sources each have one today (`substrate`, `vllm`, `sglang` roots).
History: merging 837 + 1117 + 300 commits (276 + 250 + 87 merge commits) into a 669-commit repository.

## 5. Cross-cutting plan

### 5.1 Import-path rewrite

| From | To | Files in inference-sim today (Go / non-Go) |
| --- | --- | --- |
| `github.com/inference-sim/blis-substrate/...` | `github.com/inference-sim/inference-sim/substrate/...` | 170 Go (77 non-test), 341 occurrences |
| `github.com/inference-sim/blis-vllm/...` | `github.com/inference-sim/inference-sim/engines/vllm/...` | 104 Go (12 non-test) |
| `github.com/inference-sim/blis-sglang/...` | `github.com/inference-sim/inference-sim/engines/sglang/...` | 5 Go (3 non-test) |
| (non-Go) | the same strings in `go.mod`, `go.sum`, `stack.json`, `README.md`, `CLAUDE.md`, 6 `testdata/bytegate/golden/*.json`, `scripts/test-selected-deps.sh`, `scripts/evidence/golden_equivalence.py`, `scripts/kernel/price-report.sh`, `invariants.md`, 6 workflows | 21 files |

Inside the moved trees the module's own path is the root of the rewrite: each moved package keeps its path below
the prefix (`blis-substrate/load` becomes `inference-sim/substrate/load`). Also rewrite: `//go:embed` is relative
and needs no edit; `modzip.CreateFromDir(... "github.com/inference-sim/blis-substrate" ...)` in
`substrate_test.go` and the `mod` constants in `contracts/architecture_test.go`, `tools/prcheck`, `tools/modlint`
and `tools/invariants` (they build import paths by string); `go run ./validate/cmd/...` and `go test ./tools/...`
paths in workflow files and `check-runs.yaml` strings. A path-reference lint (X7: nothing under `substrate/` names
a path under `engines/`) must be in place before the engine trees land.

### 5.2 `go.mod` / `go.sum` merge

- No nested module: delete each source's `go.mod` and `go.sum` in the merge commit (or the module-boundary tests
  fail); keep inference-sim's `go.mod` as the only one.
- No new third-party module is expected. substrate needs `gopkg.in/yaml.v3`; blis-vllm needs logrus, testify,
  `gopkg.in/yaml.v3`, `pgregory.net/rapid`, `golang.org/x/sys v0.13.0` (indirect); blis-sglang needs
  `gopkg.in/yaml.v3`. inference-sim's `go.mod` already requires all of them (x/sys at v0.48.0). Confirm with
  `go mod tidy -diff` in each merge PR; do not edit `go.sum` by hand.
- Drop the three `require` lines (and the `exclude blis-vllm v0.32.0`), keep the single `replace` of the router
  fork (X11); the fork stays a separate module reached by `replace` (`llm-d-router`).
- The language level of the substrate rises from `go 1.24` to inference-sim's `go 1.27.2`; run
  `go vet ./substrate/...` and the catalog determinism tests (`derive_graph.py --check`) to see any difference.
- Go toolchain: the composite action `.github/actions/go-toolchain` and `contracts/toolchain` move in-tree, so
  inference-sim's 13 `uses: .../blis-substrate/.github/actions/go-toolchain@b6748ca9` references become
  `./.github/actions/go-toolchain`.

### 5.3 Re-pointing `stack.json`, `guides.lock` and the external pins

| Pin | Where | Today | After row 2 |
| --- | --- | --- | --- |
| `stack.json` `modules` | inference-sim | four modules (`blis-sglang`, `blis-substrate`, `blis-vllm`, `llm-d-router` with `replaces`) | one module (`llm-d-router`); `engines[]` (vllm 0.33.0 `4ba787ec`, sglang 0.5.23 `297e54fd`) and `router` stay; `internal/stack/stack.go` and the `stack` job in `ci.yml` read the module list; row 3 then replaces engine versions by commits |
| `guides.lock` | inference-sim | one line: the llm-d guides commit `4427f55c` | unchanged (fixtures under `sim/llmd/testdata`); a path edit only if the fixtures move |
| `.github/tags.lock` | inference-sim (57 tags) | tags of inference-sim only | blis-substrate/vllm/sglang tags (5/5/1) are not carried over; they stay readable in the archived repositories |
| accuracy-dashboard `.github/stack-pins.env` | `SIM_REF` (inference-sim head), `SUBSTRATE_REF b6748ca9`, `ROUTER_REF`; `checks.yml` reads `stack.json` `modules[]` for a path ending `/blis-substrate`; `score-contracts.yml` and `api-nightly.yml` clone `blis-substrate` and fetch `blis-vllm/<ref>/fields.json` | substrate and vllm by clone/raw URL | `SUBSTRATE_REF` removed; the substrate checkout becomes `SIM_REF`'s `substrate/` subtree; `fields.json` URL becomes `inference-sim/<ref>/engines/vllm/fields.json`; the `stack.json` module lookup is replaced by the in-tree path |
| blis-config-search `pins.env` | `BLIS_REF v0.18.2`, `BLIS_SHA`, `SUBSTRATE_REF`, `VLLM_REF`, `SGLANG_REF` (pseudo-versions) | three module pins | `BLIS_REF` only; `scripts/clone_pinned.sh` calls in `pages.yml`, `pin-compat.yml`, `checks.yml` that clone `../blis-substrate` read `catalog/` and `registry/` from `<inference-sim checkout>/substrate/` instead; `scripts/blis_pin.py` and its test change |
| shared workflows | config-search `blis.yml` uses `shared-pr-checks.yml@f9f3c9327794` (substrate release v0.14.1); blis-vllm and blis-sglang use `@883a2709c250`; inference-sim uses `@b6748ca9d757` | commit-pinned in four repositories | re-point each to inference-sim's copy at a pushed commit; an archived repository still serves its commit-pinned workflows but takes no fixes (to confirm) |

### 5.4 CI: workflows to path-filter

Three different path-filter systems exist today: inference-sim's `scripts/ci-changes.sh` (fail-closed: a path no
class names turns every job on; `scripts/ci_changes_test.go` checks the classes against `go list -deps -test`),
blis-substrate's `tools/changedjobs` (a `changes` job in `ci.yml`) and blis-vllm's `changed_jobs.py` /
blis-sglang's `ci-light-select.sh`. Consolidate into `ci-changes.sh`.

| Workflow (source) | Becomes | Filter |
| --- | --- | --- |
| substrate `ci.yml` jobs `go`, `lint`, `contracts*`, `kernel*`, `catalog`, `registry`, `ledger`, `mutants` | jobs of inference-sim `ci.yml` | `substrate/**` and the directories each job's `go list -deps` closure names |
| vllm `ci.yml` (`go-build`, `go-test-*`, `go-race`, `go-bench`, `oracle-*`, `packs-against-vllm`, `metrics-manifest`, `goldens-reviewed`) | jobs | `engines/vllm/**` plus `substrate/contracts/**` and `substrate/kernel/**` (what the engine imports) |
| sglang `ci.yml` (`oracle-*`, `treecore-diff`, `fields`) and `mutation.yml` (already `paths:`-filtered) | jobs | `engines/sglang/**` plus the same substrate paths |
| substrate `ledger.yml`, `ledger-candidate.yml`, `rederive.yml` (already `paths:`), `nightly*.yml`, `acceptance-refresh.yml` | keep as separate workflows; move under inference-sim's `.github/workflows/` with `paths: substrate/**` | their `gate-paths` lines must equal the workflow's `paths:` (prcheck `status`) and `.github/gates.yaml` |
| `ci-light.yml` x3 (docs-only fast path) | one `ci-light.yml` | a docs-only change still needs a result for each required name |
| `shared-pr-checks.yml`, `shared-nightly.yml`, `blis.yml` x4 | `blis.yml` of inference-sim calls its own copy; the other repositories re-point | commit-pinned by `uses: ...@sha`; the inner workflow cannot be edited and referenced at the same sha, so use two PRs |
| `private-names.yml` x4 | one | all paths; no filter |
| `mutation.yml`, `oracle-traces.yml`, `recorded-logs.yml` (dispatch/cron) | keep, path-aware names | |
| required checks in the ruleset | maintainer edit | switch the 7 names to the aggregate job `required` (it passes when a filtered job is skipped); the ruleset is a repository setting, which an agent must not change |

### 5.5 Invariants, releases, retiring

- The invariant registry (`substrate/contracts/invariants/*.yaml`) states "Runs in" by repository; restate by
  directory (`substrate/`, `engines/vllm`, `engines/sglang`, router fork). A registry test checks that the
  `test:` strings exist, so run it after each merge PR.
- Releases: per-engine release branches become `release-v*` branches of inference-sim (existing: `release-v0.17`,
  `release-v0.18`). blis-vllm's `release-v0.32.0` and the `v0.33.0-blis.1` tag stay in the archived repository.
  Tag pushes and branch creation are maintainer actions (guardrail), so the PRs name them rather than do them.
- Retire (maintainer, after the transfer): archive the three repositories with a pointer to inference-sim; the
  README of each gets a one-line pointer in a final PR first.

## 6. Pull-request sequence

All pull requests are drafts. "Base" is the branch the PR is cut from and targets. Rows are in dependency order
(Table W: 1, then 27, then 2, then 5 and 3).

### Row 27: blis-vllm compatibility code removed (depends on 1)

| PR | Repo / base | Content | Gate |
| --- | --- | --- | --- |
| 27.1 | blis-vllm / `main` | port the seven packages `vllmengine` uses, plus `rules/` into `core/` (vllmengine imports `engineconfig`, `pack` and all of `v0_29` to `v0_33` today; whether the older packs can go is row 27's call) as v0.33.0 code; do not copy unchanged (requirements). Import rewrite `blis-vllm/compat/X` to `blis-vllm/core/X` with `gofmt -r` / `sed`; `compat/` stays | `go test -p 4 ./...`; every oracle tier (`oracle-tier2`, `-scenarios`, `-inertness`, `-fuzz`) |
| 27.2 | inference-sim / `main` | decision PR: per package of `build`, `kv`, `lora`, `contract`, `dplb`, `prefix`, `kvkey`, `kvtransfer`, `nixl`, whether it is ported to `core/` (kv and lora already have `core/` counterparts) or replaced by the `vllmengine` path; rewrite `cmd/engine_build.go`, `cmd/result_inputs.go`, `tools/harness/*`, `internal/stack`, `scripts/kernel/*` and the 92 test files; keep `testdata/bytegate` goldens byte-identical (INV-6) | `go test -p 4 ./...`; gofmt; bytegate goldens unchanged |
| 27.3 | blis-vllm / 27.1 | delete `compat/` and `rules/`; update `kerneltests/`, `tools/harness`, root tests, regenerate `surface.json` / `fields.json` / `kernel_impls.json` with `gen_*.py` | `go list -deps ./...` lists neither; oracle tiers pass at v0.33.0 |
| 27.4 | inference-sim / 27.2 | re-point `stack.json` blis-vllm to the 27.3 head (pseudo-version + commit); `scripts/test-selected-deps.sh` shards (named `compat/kernelmodel`) change; `ci.yml` selected-deps shard labels | `stack` job; full `ci.yml` |

27.2 and 27.4 are inference-sim pull requests that the plan's row 27 (repository: blis-vllm) does not list; the
row's sub-agent needs access to inference-sim.

### Row 2: the migration (depends on 1 and 27)

| PR | Repo / base | Content | Notes |
| --- | --- | --- | --- |
| 2.1 | fork / `llm-d-r` | add `blisembed/` and `blisembed/embedtest/` (copy of `contracts/embed`, `contracts/conformance/embedtest` at one substrate commit); rewrite `pkg/embed` imports; rename X7 test; update the two apidiff scripts, `hosting-lint.yml`, `fork-policy` toolchain/deferral reads; drop the substrate require; `go mod tidy` | budget 404 to 401; merge commit (RTR-1); commits signed and with an `Assisted-by` line (fork rule) — see risk 2 |
| 2.2 | inference-sim / `main` | `replace` to the 2.1 head; 13 files import `.../blisembed` (`cmd/result_inputs.go` and 12 in `sim/llmd`, tests included); `stack.json` router entry | `TestSupportedTypesAreHostedByTheFork`, `sim/llmd` tests |
| 2.3 | blis-substrate / `main` | delete `contracts/embed` and `embedtest`; edits of section 2.2 (architecture test, invariants, `.golangci.yml`, `check-runs.yaml`, review-set id) | needs the SUB-1 accept-break once |
| 2.4 | inference-sim / `main` | CI first: classes for `substrate/` and `engines/` in `ci-changes.sh` + its test; import-graph lint (`go list`, required) and the X7 path-reference lint; module-size check; port `shared-*` workflows and `go-toolchain` action in-tree (unreferenced) | no code moves yet; keeps every merge below inside the filter |
| 2.5 | inference-sim / 2.4 | substrate subtree merge to `substrate/` (history-preserving, see below); import rewrite (170 files); delete its `go.mod`/`go.sum`; `stack.json`; invariants "Runs in"; `check-runs.yaml` strings; workflow ports | the largest PR; do not squash |
| 2.6 | inference-sim / 2.5 | blis-vllm to `engines/vllm`; same steps (104 files); `scripts/test-selected-deps.sh`; the 18 jobs path-filtered | module-size gate not exceeded (45 MB) |
| 2.7 | inference-sim / 2.6 | blis-sglang to `engines/sglang`; **only after the golden-trace decision (section 4)**; `core/metrics/testdata` handling | module-size gate |
| 2.8 | accuracy-dashboard, blis-config-search / `main` | re-point pins (section 5.3), shared workflow refs, `clone_pinned.sh` paths | draft until inference-sim has the merged commit |
| 2.9 | the three repositories / `main` | README pointer to inference-sim; no code | then a maintainer transfers issues, resolves the 98 open pull requests, archives (not an agent action) |

History-preserving merge, per source repository: clone the repository, rewrite its history under the prefix
(`git filter-repo --to-subdirectory-filter substrate` and the same for `engines/vllm`, `engines/sglang`), then
`git merge --allow-unrelated-histories` into the 2.4 branch. `git subtree add` without `--squash` keeps the
commits but not their paths (so `git log -- substrate/` shows only the merge); the rewrite changes every SHA, so
keep the old-to-new map (`.git/filter-repo/commit-map`) with the PR. Every SHA quoted in an existing pin, comment
or evidence file names an old commit that exists only in the archived repository.

### Row 5 and row 3 (depend on 2; row 3 also on 25)

| PR | Base | Content | Why it is simpler after row 2 |
| --- | --- | --- | --- |
| 5.1 | inference-sim `main` after 2.7 | lowering out of `substrate/catalog/scripts/derive_graph.py` into `engines/vllm` (and `engines/sglang` if the deriver holds any); the deriver writes checkpoint facts only | one repository: deriver, engine and `--check` in one PR instead of three pins |
| 5.2 | 5.1 | delete `substrate/contracts/rules/`; model values to graph fields; restate invariants | `rules/` of blis-vllm is already gone (row 27) |
| 5.3 | 5.2 | remove `onboard --plan`, its tests and docs | |
| 3.1 | inference-sim `main` after 2.7 and 25 | `gen_surface.py`, `gen_kernel_impls.py`, `gen_fields.py` work at any commit (paths now `engines/*/tools`); oracle environment locked to the commit | |
| 3.2 | 3.1 | upgrade report; commit distance in grading (dashboard, separate PR) | |
| 3.3 | 3.2 | `stack.json` names commits not versions; `inference-sim version`; scenario `engine.version` field removed (blis-substrate#204 review set) across `testdata/kernel/aisimulate` scenarios and `substrate/contracts/spec` | scenarios and loader in one module |
| 3.4 | 3.3 | upgrade blis-vllm to vLLM `b582592d5a62` | |

## 7. Risks (ordered by cost if missed)

1. **Module size (SUB-13).** The merged module is about 271 MB tracked against a 100 MB limit; blis-sglang's
   135.5 MB of golden traces is the cause. If not decided before 2.7, the merge fails the new size check, or the
   check is quietly weakened.
2. **The hosting contract's move breaks the fork's own required checks.** The fork's toolchain and X20-deferral
   reads, both apidiff scripts and the X7 test all assume the contract is in a pinned substrate; the fork's
   rules also demand signed commits with an `Assisted-by` line, which an agent's commits cannot satisfy, so 2.1
   needs a maintainer to commit or to confirm the deferral. Ordering matters: 2.1, then 2.2, then 2.3.
3. **Row 27 is bigger than its row.** inference-sim imports nine `compat/` packages, six of which `vllmengine` does
   not (`build`, `contract`, `dplb`, `kv`, `lora`, `prefix`; 104 files, `cmd/engine_build.go` registers the KV store and adapter registry from `compat/kv` and `compat/lora`).
   Removing `compat/` changes inference-sim's behaviour path and its byte-identical goldens, and needs inference-sim
   pull requests (27.2, 27.4).
4. **CI continuity.** The ruleset names matrix contexts, the shared workflows are commit-pinned in four
   repositories, and three path-filter systems merge into one fail-closed script. A required name that no job
   emits blocks every merge; the ruleset is a maintainer change.
5. **Issue and pull-request transfer.** 98 open pull requests cannot be transferred; issue numbers change and are
   cited in `contract-review-set`, accept-break ids, `m31-carried.tsv`, comments and invariants.
6. **History volume.** 2,254 commits (613 merge commits) enter inference-sim with rewritten SHAs; `git bisect`,
   old pins and the evidence files that quote SHAs need the old-to-new map.
