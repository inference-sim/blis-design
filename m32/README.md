# BLIS M3.2: working requirements

Working material for the M3.2 release, started 2026-11-18. This branch is for
reading and editing; it is never merged into `main`, which holds the standing design.

Start with [`requirements.md`](requirements.md). Its Terms section defines the project's terms. Section DC lists what
M3.2 builds for [design v2.3.0](https://inference-sim.github.io/blis-design/v2.3.0/blis-target-design.html).
Section 0 lists what M3.1 left for M3.2. Each requirement carries one of three labels, defined in the requirements.

For a one-page overview of the data sources and the calibration process, download
[`data-and-calibration.html`](data-and-calibration.html) and open it in a browser; GitHub shows HTML files as
source only.

**Table R. Each evidence note backs one section of the requirements.**

| File | What it backs |
|---|---|
| [`evidence/INVENTORY.md`](evidence/INVENTORY.md) | What vLLM, SGLang and PyTorch publish as performance data, and where (§1) |
| [`evidence/SETTINGS-PROVENANCE.md`](evidence/SETTINGS-PROVENANCE.md) | Where each new source records its workload, GPU, model and engine settings (§2) |
| [`evidence/COVERAGE-FUNNEL.md`](evidence/COVERAGE-FUNNEL.md) | Why 238 InferenceX anchor units are scored of 13,182 in scope, and how many configiq units could be (§3A) |
| [`evidence/CONFIGIQ-FINDINGS.md`](evidence/CONFIGIQ-FINDINGS.md) | How Red Hat's configiq rows are produced, and which settings can be recovered (§3C) |
| [`evidence/NEW-MODELS-GB200.md`](evidence/NEW-MODELS-GB200.md) | What Mistral-Large-4 and Inkling-2-Small need on GB200: no new kinds of layer expected, and kernels with no GB200 measurement (DC4) |

The raw downloads behind the notes are not in the repository.

Also here:
- [`plan.html`](plan.html): the M3.2 plan, generated from `plan.preamble.md`, `requirements.md` and
  `plan.appendix.md` by [`tools/build_plan.py`](tools/README.md). Never edit it by hand.
- [`m31-carried.tsv`](m31-carried.tsv): the 150 M3.1 plan issues still open, each with its plan item and any note
  from the M3.1 review (§0.4).

## How to contribute

Push to the `m32` branch, or open a pull request into `m32` for a proposal the team should review first. Mark each
requirement with a label from the requirements.
