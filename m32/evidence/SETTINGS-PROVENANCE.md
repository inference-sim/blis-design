# Where each new source records its run settings

Checked 2026-11-18, by reading each source's own code and data. It backs requirements §2.3.

## vLLM CI perf API (`ci.vllm.ai/api/perf`)

- A row has a date, model, device, `tp`, `conc`, `isl`, `osl`, precision, image and metrics. It has no run id.
- `tp` is TP × DP: `perf-eval`'s `lib/ingest_perf.py` calls it the "effective parallel degree", and divides
  throughput by it.
- Latencies are in seconds: the ingest code divides each `*_ms` field by 1000.
- The engine commit is the image tag `vllm-release-repo:<sha>`. A few rows are tagged `nightly` or `v0.25.0`, so
  they are not pinned to a commit.
- The serve flags and the workload are in `vllm-project/perf-eval`'s `workloads/<model>_<gpu>.yaml`, at the git
  revision current on the row's date: `serve_args`, and the `vllm_bench` block (random dataset, input and output
  lengths, 512 prompts, maximum concurrency, 3 repetitions, warm-up count).
- The client is `lib/run_vllm_bench.sh`: `vllm bench serve` with `--ignore-eos` and `--save-result` per repetition.
  `lib/aggregate_perf.py` merges the repetitions; which statistic it takes is still to confirm. The seed and range
  ratio are `vllm bench`'s defaults at that commit, also to confirm.
- Host and environment: `lib/gpu_profiles.yaml` (H200 runs in Docker; B200 runs natively on Kubernetes; environment
  variables `VLLM_DEEP_GEMM_WARMUP=skip`, and `NCCL_CUMEM_HOST_ENABLE=0` on B200). The Docker arguments are in
  `lib/server.sh`.
- The server logs and Nsight traces are Buildkite artifacts, which are private (HTTP 403). So the engine settings
  vLLM resolved are not visible.

## SGLang nightly `consolidated-metrics` artifacts and job logs (`nightly-test-nvidia.yml`)

- The artifact `consolidated-metrics-<run_id>` has `commit_sha`, `gpu_config`, `model`, `variant` and `benchmarks[]`.
  Its `server_args` field is empty.
- The job log, kept 90 days, has the full resolved `server_args` dump for each server launch, and sampled prefill
  and decode batch lines. Older logs return HTTP 410, so they must be archived as they appear.
- The GPU is the job's runner label (for example `8-gpu-h200`); the commit is the run's `head_sha`.
- The client is `python/sglang/benchmark/one_batch_server.py`: one static batch, random dataset, seed 42,
  `ignore_eos` on by default, a warm-up unless `--skip-warmup`, and an optional warm-up of the prefix cache. It
  reports `latency` and `last_ttft`, the TTFT of the batch's last request. That is not the mean TTFT that vLLM and
  InferenceX report.

## SGLang profiler traces (`github.com/sgl-project/ci-data`, `traces/<run_id>/...`)

- `scripts/ci/utils/publish_traces.py` published them, with the commit message "Nightly traces for run `<run_id>`
  at `<run_number>`".
- The run id is an `sgl-project/sglang` Actions run. For example, 29787916991 is a "Release Branch Cut" dispatch
  that runs the nightly, at `head_sha` `8905cbd4`. The run's jobs give the runner labels, and so the GPUs. So a
  trace's commit can be recovered.
- Profiling was removed from the nightlies on 2026-08-06 (sgl-project/sglang#33832), so no new traces appear. The
  traces date from about 2026-05 to 2026-07, all on SGLang releases before v0.5.20 (2026-09-18). blis-sglang models
  v0.5.23 (2026-10-29).
- Their job logs have expired, so the server arguments come from the nightly test definitions at the `head_sha`.
- The trace itself records `deviceProperties` (the GPU), `distributedInfo` (world size and process groups), and
  the batch size and input length in its file name. It covers rank 0 only.
