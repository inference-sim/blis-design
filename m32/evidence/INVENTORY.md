# vLLM / SGLang / PyTorch performance data inventory (2026-11-18)

Inventory only; nothing ruled out. "Verified" = queried and data seen this session.
Raw samples are not in the repository.

## Serving aggregates with known config
- vLLM CI perf API https://ci.vllm.ai/api/perf (no auth; params model, device, tp, conc, start, source).
  Verified. ~7,600 rows 2026-06-14..today, nightly; H200 1,718, B200 547, B300 143, GB300 5, AMD rest; no H100.
  vllm bench serve, random, ignore-eos; mostly 8192/1024 @ c128; some 50000/1000 @ c2-64.
  mean/median/p99 TTFT, TPOT, ITL; throughput. Image = exact vLLM commit. Latency units look like seconds (inferred).
  DP/EP/MTP/KV dtype only in vllm-project/perf-eval workloads/<model>_<gpu>.yaml (join by git history at row date).
- SGLang nightly consolidated-metrics artifacts (sgl-project/sglang workflow 206785642). Verified.
  51 runs 2026-08-21..11-17, 90-day retention, commit_sha per run; 5,187 rows; H200, B200, GB300.
  bench_one_batch_server static batch (bs 1/8/16, 8192/512); latency, TTFT, throughputs; server_args empty.
- SGLang AMD MI355X P/D nightly artifacts (workflow 301165031): 1p1d/2p1d EP16, concurrency sweep; 30-day retention.
- llm-d Prism archive (llm-d/llm-d-prism public/data/archive/llmd_results/llm-d-benchmarks.json):
  114 Llama-3.1-70B H100 records 2025-09, 30 P/D; no vLLM version.

## Step / host / scheduler level
- SGLang ci-data traces (github.com/sgl-project/ci-data, ~105 GB, last push 2026-07-21). Verified repo; agent opened 2 traces.
  Kineto traces rank 0, EXTEND + DECODE per bs/il; ~45 model/variant dirs (DeepSeek V3.2/V4-Pro, Kimi, GLM, gpt-oss, MiniMax, Qwen3.5).
  Step spans, scheduler host spans, cudaGraphLaunch, every GPU kernel. No commit is recorded in the trace itself; it is recoverable through the Actions run
  (SETTINGS-PROVENANCE.md).
- SGLang nightly job logs (90 days): server_args dumps, sampled Prefill/Decode batch lines.
- vLLM blog interactive pages (vllm-project/vllm-project.github.io assets/interactive_pages):
  DeepSeek-V4.1-Flash P/D wide-EP decode step breakdown DEP4..DEP32 (GB200/GB300), prefill tables, EPLB.
- vLLM perf-eval Buildkite artifacts incl. Nsight traces H200/B200: private (403).

## Kernel level
- Tritonbench nightly artifacts (meta-pytorch/tritonbench workflow 255401705), 90-day retention. Verified.
  H100 + MI350; 3,475 metrics/run: op[shape-backend] latency/tflops; fp8 gemm variants, grouped gemm,
  attention variants, norms, rope, launch_latency; env commits, clocks, power.
- PyTorch OSS benchmark DB (ClickHouse oss_ci_benchmark_v3): vLLM benchmark, operator benchmark, gpt-fast,
  Helion B200. HUD 429 to scripts; query API needs Dev Infra credentials.

## Declared facts / configs
- vLLM fused_moe configs (169 for H100/H200/B200/GB200); SGLang triton MoE configs (405 files).
- SGLang AgentX launch configs (docs/src/snippets/agentx), InferenceX-mirrored Dynamo-SGLang P/D.
- LMSYS blog P/D tables: DeepSeek-V4.1-Flash 8xH200 1P1D; GLM-5.3-Flash H200 3P1D NIXL (73 rows, commit pins).

## Other
- tools/sglang-simulator in SGLang: peer simulator (AISimulate backend, replay table).
- vllm bench forward (PR #61339): tool, not data.
