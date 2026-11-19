# configiq: how its rows are produced, and how to recover their settings

Checked 2026-11-18. It backs requirements §3C.

Sources, all public:
- the GitHub repositories `redhat-performance/configiq` at `009919e` and `openshift-psap/forge` at `673b4dfa`;
- `performance-dashboard`, `benchconf`, `LLM-inference-benchmark-guide` and `psap-control-center`;
- the Hugging Face dataset's revision history.

Two things were checked by hand: the parser's regular expression (configiq
`scripts/tested_models/dataset_common.py`, lines 62 to 66), and forge's `cpt.d/cpt.yaml`, which sets
`enable-prefix-caching` and `kv-cache-dtype`.

Names used here:
- **forge** is Red Hat's open-source benchmark launcher.
- **Model Furnace** is an earlier, private Red Hat launcher.
- **CPT** is forge's per-model test matrix.
- **GuideLLM** is the load generator all three writers use.

## What BLIS assumed that is not so

1. **A blank is not in general "flag not passed".** The publisher extracts each setting from a free-text CSV
   column, `runtime_args`, with the pattern `(?:^|[;\s])(?:--)?NAME\s*(?:=|:)\s*([^;\s]+)`.
   - It matches `key: value` and `--key=value`.
   - It returns a blank for `--max-model-len 8192`, for a bare flag, for `no-enable-...: True`, and for names written
     with underscores.
   - A blank means "not passed" only for rows forge wrote, because forge joins its arguments as `key: value` pairs
     separated by `; ` (forge `test_phase.py`, lines 578 to 584).
2. **Three writers feed one private CSV.** The dataset is a weekly, filtered copy of a private CSV
   (`consolidated_dashboard.csv` in a private S3 bucket). Its writers are forge, manual JSON imports (from
   `performance-dashboard`) and Model Furnace. The filter keeps 10 approved models, version labels of the form
   `vLLM-x.y.z`, and the classification columns only.
3. **`prefix_caching` is passed through, not parsed.** forge fills it. Older writers left it blank even when prefix
   caching was off.
4. **The ledger's forge presets miss `cpt.d/cpt.yaml`.** That file sets the KV-cache dtype, and enables prefix
   caching from commit `239be42d` (2026-09-28). The presets also miss the `/v1/completions` request type forge uses
   for gpt-oss-120b.
5. **The dataset is not append-only.** 444 rows labelled `vLLM-0.31.0` were removed between Hugging Face revisions
   `69389b1` and `12afd88`. Pin a revision.

## The rows by writer

**Table C1. The current revision's whole-run rows fall into three families, recognised by their request type.**

| Family | Signature | Rows / units | Writer |
|---|---|---|---|
| A | request type starts `/v1/`, prefix caching on | 800 / 779 (H200 205, B200 168, MI355X 406) | forge's CPT, GuideLLM 0.7.4 or 0.8.1, vLLM 0.26 to 0.33 (a few 0.22 and 0.24) |
| C | request type `chat_completions` or `text_completions` | 143 / 128 (H200) | manual imports |
| D | request type blank | 830 / 803 | Model Furnace and older manual imports, vLLM 0.11 to 0.24 |

The current revision has 1,773 whole-run rows (1,710 units) and 1,036 per-turn slices. No family B was found. The
ledger's pinned revision, `21cc6eb`, has 1,702 units.

## Each setting: its value or rule, its evidence, and how sure

- **`gpu_memory_utilization`.** Family A: 0.92, from forge's base arguments (`rhaiis.yaml`), on every row. Families
  C and D: mostly 0.92. A blank would be vLLM's default, 0.9 through v0.19.1 and 0.92 from v0.20.0, but that a
  blank means the default is not proven.
- **`max_seq_len`.** Family A never passes it, so it is the model's configured length. Family D's 8192 and 10000 are
  Model Furnace defaults; 34816, 67584 and 110000 are manual long-context runs.
- **`max_num_seqs`.** forge never passes it, so it is vLLM's default: 1024 on H200 and B200.
- **`max_num_batched_tokens`.** vLLM's default: 8192 on H200, and from v0.28.0 16384 on parts with 160 GiB or more
  (B200, MI355X, MI300X).
- **Chunked prefill.** Never configured, so vLLM's default. It is blank everywhere, because the pattern cannot
  match a bare flag.
- **Precision and weight quantization.** Family A never passes them, so they come from the model's dtype and the
  checkpoint.
- **`kv_quantization`.** Family A: from `cpt.yaml` and `models.yaml`'s `kv-cache-dtype`.
- **`prefix_caching`.** Family A: on, from the CPT; before 2026-09-28 the base arguments turned it off. Family D,
  when blank: likely off when memory utilisation is 0.92 and `max_seq_len` is 8192 or 10000 (inferred, medium
  confidence).
- **Data and expert parallelism.** forge sets neither for the 8 dataset models it ran; it sets expert parallelism
  only for Maverick-w4a16, Qwen3-235B, nemotron3ultra and Inkling. Families C and D are unknown: the CSV has a DP
  column the publisher drops (a case mismatch), and `performance-dashboard` computes GPUs as TP × DP. A C or D row
  with TP 1 may still use several GPUs.
- **The GuideLLM frame.**
  - The profile is concurrent, and each run is limited by a maximum duration. On forge's main branch:
    - 450 s, with no warm-up or ramp-up, from 2026-06-09 to 2026-09-22;
    - 275 s, with a 35 s ramp-up, from 2026-09-22 (commit `3d8b5373`);
    - a warm-up of 75 from commit `29c1f3c1`, and none from 2026-11-06.
  - Little's law on each concurrency-1 row confirms the durations: 275 s for family A; 450 s for family D, and
    600 s for vLLM 0.13 and older, and for 8k/1k workloads on vLLM 0.20 and older.
  - Requests stream, `max_tokens` is the sampled length, `ignore_eos` is on, the default endpoint is
    `/v1/chat/completions`, the seed is 42, and prompts are synthetic text with `workloads.yaml`'s limits.
  - forge's GuideLLM versions: v0.6.0 from 2026-06-02, v0.7.4 from 2026-09-21, v0.8.1 from 2026-10-12.
- **Hardware.** The H200 clusters Hera and Zeus have one node of 8 H200s each. Others are Athena, Janus, a B200
  cluster and an MI355X cluster. The GPU count is TP. The dataset drops the cluster tag and keeps only the
  accelerator. The interconnect is not stated.
- **Environment.** `VLLM_ROCM_USE_AITER=1` on AMD; `FLASHINFER_CUBIN_DIR` on B200; `NCCL_DEBUG=WARN` when TP is
  above 1; `/dev/shm` of 64 GiB.
- **Image.** An upstream `vllm/vllm-openai:vX`. The dataset's `version` is a free-text label, separate from the image
  tag.
- **From row to run.** The private CSV has a uuid, MLflow ids, GuideLLM times, the image tag and the GuideLLM
  version. The published dataset has none of them.
- **forge's history.** `projects/rhaiis` starts on 2026-06-02 (commit `4edf18ac`). Models were inline in
  `config.yaml` until commit `117e2386`. Older rows come from Model Furnace or manual imports; the only public
  description of those runs is `LLM-inference-benchmark-guide`.

## What can be recovered

- **Family A** (779 units, 373 on H200 or B200): every blank, from the CPT and from vLLM's defaults per release and
  device, and the frame from `cpt.yaml`'s history (a 275 s duration).
- **Family D**, where `max_seq_len` is 8192 or 10000 and memory utilisation is 0.92: prefix caching off, and a 450 s
  or 600 s duration (medium confidence).
- **Not recoverable:** data parallelism in families C and D, the cluster, the image as opposed to the label, and the
  actual first-turn prompt length of configiq's multi-turn workloads.

## What would raise coverage and closeness

1. Read blanks by family, instead of refusing every blank.
2. Treat `cpt.yaml` and the presets as presets, matched on model, TP, KV dtype and request type, and dated by
   forge's commits.
3. Never read a blank `prefix_caching` as on.
4. Derive each unit's duration from its concurrency-1 row, and compare successful requests only: the 8000/800 rows
   have many errored requests.
5. Model the multi-turn workloads with their actual shapes (`benchconf`'s `configs/configiq/interactive-chat.yaml`:
   a first prompt of about 4,000 tokens, and 45 s between turns).
6. Treat a family C or D row with TP 1 as possibly data-parallel.
7. Ask Red Hat to publish an allow-listed `runtime_args`, the image tag, the GuideLLM version, the cluster tag, the
   start and end times, DP and the turn index; to fix the case mismatch that drops DP; and to publish more of the
   roughly 52 models the CSV holds (10 are published).
8. Pin a revision, and treat the 63 duplicated units as possibly from different clusters.
