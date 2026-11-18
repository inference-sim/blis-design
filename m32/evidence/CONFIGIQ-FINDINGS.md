# configiq: how rows are produced and how to recover their settings (2026-11-18)

Sources read (public GitHub repos): redhat-performance/configiq @009919e, openshift-psap/forge @673b4dfa,
performance-dashboard, benchconf, LLM-inference-benchmark-guide, psap-control-center, and the Hugging Face
dataset's revision history. Re-verified by hand: the parser regex (configiq
scripts/tested_models/dataset_common.py:62-66) and forge cpt.d/cpt.yaml (enable-prefix-caching, kv-cache-dtype).

## Corrections to what BLIS assumes
1. Blank is not generally "flag not passed". The publisher regex-parses the free-text CSV column runtime_args:
   (?:^|[;\s])(?:--)?NAME\s*(?:=|:)\s*([^;\s]+). It matches "key: value" and "--key=value"; it gives blank for
   "--max-model-len 8192", bare booleans, "no-enable-...: True", underscore names. Blank = not passed only for
   forge-written rows ("key: value" joined by "; ", forge test_phase.py:578-584).
2. The dataset is a filtered weekly view of a private S3 CSV (psap-dashboard-data/.../consolidated_dashboard.csv)
   with three writers: forge, manual JSON imports (performance-dashboard), Model Furnace (private). Filter:
   10 approvedModels, version label vLLM-x.y.z, CLASSIFICATION_COLUMNS only.
3. prefix_caching is a pass-through column filled by forge; older writers left it blank even with prefix caching off.
4. The ledger's forge presets miss cpt.d/cpt.yaml (kv-cache-dtype, enable-prefix-caching true from 239be42d,
   2026-09-28) and request_type /v1/completions for gpt-oss-120b.
5. The dataset is not append-only: 444 vLLM-0.31.0 rows removed between HF revisions 69389b1 and 12afd88. Pin.

## Writer families (current revision: 1,773 whole-run rows / 1,710 units; 1,036 per-turn slices)
| Family | Signature | Rows / units | Source |
|---|---|---|---|
| A | request_type starts /v1/, prefix_caching=yes | 800 / 779 (H200 205, B200 168, MI355X 406) | forge CPT, GuideLLM 0.7.4/0.8.1, vLLM 0.26-0.33 (+ few 0.22/0.24) |
| C | chat_completions / text_completions | 143 / 128 (H200) | manual imports |
| D | request_type blank | 830 / 803 | Model Furnace, older manual, vLLM 0.11-0.24 |

## Settings (value or rule, evidence, confidence)
- gpu_memory_utilization: A 0.92 (rhaiis.yaml base args; all rows). C/D mostly 0.92; blank -> vLLM default
  0.9 through v0.19.1, 0.92 from v0.20.0 (unproven that blank = default).
- max_seq_len: A never passed -> model config length. D 8192/10000 furnace defaults; 34816/67584/110000 manual.
- max_num_seqs: never passed in forge -> vLLM default (1024 on H200/B200).
- max_num_batched_tokens: vLLM default 8192 on H200; from v0.28.0 16384 on >=160 GiB parts (B200, MI355X, MI300X).
- chunked prefill: never configured -> vLLM default; blank everywhere because the regex can't match booleans.
- precision / weight quantization: A never passed -> model dtype / checkpoint.
- kv_quantization: A from cpt.yaml / models.yaml kv-cache-dtype.
- prefix_caching: A yes (CPT); before 2026-09-28 base was no-enable-prefix-caching. D blank: likely off when
  gpu 0.92 and max_seq_len 8192/10000 (medium, inferred).
- DP/EP: forge sets neither for the 8 dataset models (EP only for Maverick-w4a16, Qwen3-235B, nemotron3ultra,
  inkling). C/D unknown: the CSV has a DP column the publisher drops (case mismatch); performance-dashboard
  computes GPUs as TP x DP. Never assume tp=1 C/D rows are single GPU.
- GuideLLM: profile concurrent; constraint max_duration. Forge main: 450 s no warm-up/ramp (06-09..09-22);
  275 s + rampup 35 s from 09-22 (3d8b5373); warmup 75 from 29c1f3c1, 0 from 11-06. Little's law at
  concurrency 1 confirms: A 275 s, D 450 s (600 s for vLLM <=0.13 and 8k/1k <=0.20). Streaming, max_tokens =
  sampled length, ignore_eos true, default /v1/chat/completions, seed 42, synthetic_text with workloads.yaml clamps.
  Versions: v0.6.0 (06-02), v0.7.4 (09-21), v0.8.1 (10-12).
- Hardware: H200 clusters Hera and Zeus, one 8xH200 node each; others Athena, Janus, b200, mi355x. gpuCount = TP.
  Cluster tag dropped from the dataset (accelerator only). Interconnect not stated.
- Env: AMD VLLM_ROCM_USE_AITER=1; B200 FLASHINFER_CUBIN_DIR; NCCL_DEBUG=WARN when TP>1; /dev/shm 64 GiB.
- Image: upstream vllm/vllm-openai:vX; `version` is a free-text label separate from the image tag.
- Row -> run: private CSV has uuid, mlflow ids, guidellm times, image_tag, guidellm_version; HF has none.
- Forge history: projects/rhaiis from 2026-06-02 (4edf18ac); models inline in config.yaml until 117e2386.
  Older rows: Model Furnace (private) or manual; public description only in LLM-inference-benchmark-guide.

## Recoverable
- Family A (779 units; 373 on H200/B200): every blank from CPT + vLLM defaults per release and device;
  frame from cpt.yaml history (275 s window).
- Family D with max_seq_len 8192/10000 and gpu 0.92: prefix caching off, 450/600 s window (medium).
- Not recoverable: DP in C/D, cluster, image vs label, real turn-1 prompt length of ConfigIQ workloads.

## Levers
1. Family rule replaces "blank means refuse". 2. Read cpt.yaml and presets as presets, matched on model, TP,
kv dtype, request_type, dated by forge commits. 3. Blank prefix_caching is never "on". 4. Stop rule per unit from
the concurrency-1 row; score successful requests only (8000/800 rows have many errors). 5. Model the multi-turn
workloads with their real shapes (benchconf configs/configiq/interactive-chat.yaml: ~4,000-token first prompt,
45 s between turns). 6. Flag tp=1 C/D rows as possible DP. 7. Ask Red Hat to publish an allow-listed
runtime_args, image_tag, guidellm_version, cluster_tag, start/end times, DP, turn_index; fix the DP drop; widen
approvedModels (~52 models in the CSV, 10 published). 8. Pin a revision; treat 63 duplicated units as possibly
cross-cluster.
