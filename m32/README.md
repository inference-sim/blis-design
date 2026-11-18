# BLIS M3.2: working requirements

Working material for the M3.2 release, started 2026-11-18. It is not yet a design or a plan. This branch is for
reading and editing only; it is never merged into `main`, which holds only the standing design.

Start with [`requirements.md`](requirements.md). Section 0 lists what carries over from M3.1. Each requirement
says whether the maintainer stated it or it is a proposal open to correction.

[`evidence/`](evidence/) holds the notes the requirements cite:

| File | What it backs |
|---|---|
| [`INVENTORY.md`](evidence/INVENTORY.md) | What vLLM, SGLang and PyTorch publish as performance data, and where (§1) |
| [`SETTINGS-PROVENANCE.md`](evidence/SETTINGS-PROVENANCE.md) | Where each new source records its workload, GPU, model and engine settings (§2) |
| [`COVERAGE-FUNNEL.md`](evidence/COVERAGE-FUNNEL.md) | Why only 199 InferenceX points and about 213 configiq units are scored today (§3A) |
| [`CONFIGIQ-FINDINGS.md`](evidence/CONFIGIQ-FINDINGS.md) | How Red Hat's configiq rows are produced, and which settings can be recovered (§3C) |

Figures are as of 2026-11-18. Raw downloads behind the notes are not in the repository.

## How to contribute

Push to the `m32` branch. Mark a new requirement as **Maintainer.** (decided) or **Proposal.** (open).
