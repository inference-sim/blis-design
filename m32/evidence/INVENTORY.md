# Performance data published by vLLM, SGLang and PyTorch

Checked 2026-11-18. This is an inventory: nothing in it is ruled out. "Verified" means the source was queried and
its data seen. The raw samples are not in the repository. Abbreviations: P/D is prefill/decode disaggregation; c128
is concurrency 128; ISL/OSL are input and output lengths in tokens.

## Serving results with a known configuration

- **vLLM CI perf API**, `https://ci.vllm.ai/api/perf` (no login; query parameters `model`, `device`, `tp`, `conc`,
  `start`, `source`). Verified.
  - About 7,600 rows from 2026-06-14, added nightly: 1,718 on H200, 547 on B200, 143 on B300, 5 on GB300, the rest
    on AMD parts; none on H100.
  - Workload: `vllm bench serve` with random prompts and `--ignore-eos`, mostly ISL 8192 and OSL 1024 at c128, some
    ISL 50000 and OSL 1000 at concurrency 2 to 64.
  - Metrics: mean, median and p99 of TTFT, TPOT and ITL, in seconds (verified in `perf-eval`'s ingest code), and
    throughput.
  - Engine commit: the row's image tag names a vLLM commit, except a few rows tagged `nightly` or `v0.25.0`.
  - Data, expert parallelism, MTP and KV dtype are only in `vllm-project/perf-eval`'s
    `workloads/<model>_<gpu>.yaml`, which is joined to a row by its git history at the row's date.
- **SGLang nightly `consolidated-metrics` artifacts** (`sgl-project/sglang`, workflow 206785642). Verified. 51 runs
  from 2026-08-21 to 2026-11-17, each with its commit, kept 90 days; 5,187 rows on H200, B200 and GB300. Each row
  is one static batch from `bench_one_batch_server` (batch size 1, 8 or 16; ISL 8192, OSL 512), with latency,
  TTFT and throughputs. The artifact's `server_args` field is empty; the job log has the settings.
- **SGLang's AMD MI355X P/D nightly artifacts** (workflow 301165031): 1P1D and 2P1D layouts with 16-way expert
  parallelism, swept over concurrency; kept 30 days.
- **llm-d Prism archive** (`llm-d/llm-d-prism`, `public/data/archive/llmd_results/llm-d-benchmarks.json`): 114
  records of Llama-3.1-70B on H100 from 2025-09, 30 of them P/D; no vLLM version.

## Step, host and scheduler timings

- **SGLang profiler traces** (`github.com/sgl-project/ci-data`, about 105 GB, last pushed 2026-07-21). The repository
  was verified, and two traces were opened. Each is a PyTorch (Kineto) trace of rank 0, with separate prefill and
  decode profiles per batch size and input length, for about 45 model setups (DeepSeek V3.2 and V4-Pro, Kimi, GLM,
  gpt-oss, MiniMax, Qwen3.5 and others). Each holds step spans, scheduler spans, CUDA-graph launches and every GPU
  kernel. The trace does not record the SGLang commit, but its run id leads to it (`SETTINGS-PROVENANCE.md`).
- **SGLang nightly job logs**, kept 90 days: the full `server_args` dump, and sampled prefill and decode batch lines.
- **vLLM blog pages** (`vllm-project/vllm-project.github.io`, `assets/interactive_pages`): for DeepSeek-V4.1-Flash
  P/D with wide expert parallelism on GB200 and GB300, decode step time split into MoE and other work for 4 to 32
  data-parallel ranks, prefill tables, and the effect of expert load balancing.
- **vLLM perf-eval Buildkite artifacts**, including Nsight traces on H200 and B200: private (HTTP 403).

## Kernel timings

- **Tritonbench nightly artifacts** (`meta-pytorch/tritonbench`, workflow 255401705), kept 90 days. Verified. H100
  and MI350; 3,475 metrics per run, each an operator, shape and backend with its latency and TFLOPS. They cover
  FP8 GEMM variants, grouped GEMM, attention variants, norms, rope and launch latency, and record the software
  commits, clocks and power.
- **PyTorch's benchmark database** (ClickHouse table `oss_ci_benchmark_v3`): vLLM benchmark, operator benchmark,
  gpt-fast and Helion on B200. The HUD pages refuse scripted requests (HTTP 429), and the query API needs
  credentials from PyTorch Dev Infra.

## Declared facts and configurations

- MoE tuning configs: vLLM has 169 for H100, H200, B200 and GB200; SGLang has 405 Triton MoE configs.
- SGLang's AgentX launch configs (`docs/src/snippets/agentx`): Dynamo-SGLang P/D launches, mirrored from InferenceX.
- LMSYS blog P/D tables: DeepSeek-V4.1-Flash on 8 H200s in 1P1D, and GLM-5.3-Flash on H200 in 3P1D over NIXL (73
  rows, with commit pins).

## Other

- SGLang's `tools/sglang-simulator`: a simulator like BLIS, with an AISimulate backend and a replay table.
- `vllm bench forward` (vllm-project/vllm#61339): a tool that times one forward pass, not data.
