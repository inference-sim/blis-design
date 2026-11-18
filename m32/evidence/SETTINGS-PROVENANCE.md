# Where each M3.2 dataset's run settings live (checked 2026-11-18)

## vLLM CI perf API (ci.vllm.ai/api/perf)
- Row: date, model, device, tp, conc, isl, osl, precision, image, metrics. No run id.
- `tp` is TP x DP ("effective parallel degree", perf-eval lib/ingest_perf.py --tp help). Throughput is divided by it.
- Latencies in seconds (ingest divides *_ms by 1000). Verified in code.
- Engine commit: image tag vllm-release-repo:<sha>; some rows "nightly"/"v0.25.0" (unpinned).
- Serve flags + workload: vllm-project/perf-eval workloads/<model>_<gpu>.yaml at the git revision live on the row's date
  (serve_args; vllm_bench configs: dataset random, input/output len, num_prompts 512, max_concurrency, repetitions 3, num_warmups).
- Client: lib/run_vllm_bench.sh: vllm bench serve, --ignore-eos, --save-result per repetition; repetitions merged by
  lib/aggregate_perf.py (statistic to confirm). Seed and range ratio: vllm bench defaults at that commit (to confirm).
- Host/env: lib/gpu_profiles.yaml (H200 queue, docker; B200 k8s native runtime; env VLLM_DEEP_GEMM_WARMUP=skip,
  NCCL_CUMEM_HOST_ENABLE=0 on B200). Docker args in lib/server.sh.
- Server logs and Nsight traces: Buildkite artifacts, private (403). Resolved engine config is not visible.

## SGLang nightly consolidated-metrics + job logs (sgl-project/sglang nightly-test-nvidia.yml)
- Artifact consolidated-metrics-<run_id>: commit_sha, gpu_config, model, variant, benchmarks[] (server_args empty).
- Job log (90 days): full resolved server_args dump per launch; Prefill/Decode batch lines (sampled).
- GPU: job runner label (8-gpu-h200 etc.). Commit: run head_sha.
- Client: python/sglang/benchmark/one_batch_server.py: one static batch, dataset random, seed 42, ignore_eos on by
  default, warm-up unless --skip-warmup, optional cache-hit warm-up. Reports latency and last_ttft (TTFT of the
  batch's last request, not a mean) - metric definition differs from the vLLM/InferenceX means.
- Logs older than ~90 days return 410; harvest continuously.

## SGLang ci-data traces (github.com/sgl-project/ci-data traces/<run_id>/...)
- Published by scripts/ci/utils/publish_traces.py; commit message "Nightly traces for run <run_id> at <run_number>".
- run_id is a sgl-project/sglang Actions run (e.g. 29787916991 = Release Branch Cut dispatch that calls the nightly;
  head_sha 8905cbd4). Jobs list gives runner labels (GPU). So trace -> commit is recoverable.
- Profiling removed from nightlies 2026-08-06 (#33832): no new traces. Range ~2026-05..07 (SGLang before v0.5.20,
  2026-09-18; blis-sglang models v0.5.23, 2026-10-29).
- Their job logs are expired; server args come from the nightly test definitions at head_sha.
- Trace itself: deviceProperties (GPU), distributedInfo (world size, groups), bs/il in file name, rank 0 only.
