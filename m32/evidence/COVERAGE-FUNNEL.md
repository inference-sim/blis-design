# Why only ~200 points are scored (checked 2026-11-18)

Snapshot: accuracy-dashboard origin/main data/latest/summary.json, 2026-11-17_blis-v0.17.1_ix-api-2026-11-17
(simulator v0.17.1, engine vLLM 0.32.0; before M3.1's SGLang field list).

## InferenceX funnel
1. Ledger: 82,347 units from db-dump/2026-09-28 (+16 supplement records). vLLM 40,941, trt 18,034, sglang 14,010.
2. Not in the ledger at all: rows published after the dump. The API serves 1,287 in-scope (non-AMD) rows dated
   after 2026-09-26; 794 of them single-node vLLM/SGLang (b300 269, b200 201, gb300 95, h200 89, gb200 70, h100 32).
3. Dashboard denominator = anchor role only: 20,364 units (ledger.yaml cut-points; anchor 20% of new units,
   40% of the HELD legacy side). Fit/select/validate/held units are not on the headline by design.
4. AMD out of scope: 7,182 anchors. In scope: 13,182.
5. 180-day window (api.WINDOW_DAYS, Discussion #15 "Retention"): 12,491 in-scope anchors are outside it, and that is
   their only reason. Months: 2025-10 6,449; 2025-11 2,276; 2025-12 1,246; 2026-01..09 ~2,400.
   - The API still serves ~1 row per config (latest), back to 2025-10: 1,698 in-scope served rows are older than
     the window. vLLM server logs for out-of-window rows return 200 (ids 96001 2026-02-25, 97040 2026-03-27).
   - Superseded older measurements are not served by the API; only the dump has them (log availability unknown).
   - Non-vLLM rows: /server-log returns 404 (by design, vLLM logs); SGLang launch comes from job log or the
     recipe script at the run's commit (pull.freeze_launch_command).
6. In window: ~691 in-scope anchors; 199 graded (all G4, vLLM). Blockers: sglang no field list 186 (109 alone);
   dynamo-router 252; trt engine 111; field_not_modelled long tail (data_parallel_rpc_port 76, NCCL/flashinfer envs).

## configiq
- 1,702 units (H200 1,031, MI355X 417, B200 226, MI300X 28), vLLM 0.13-0.33.
- chunked_prefill_enabled blank in all 1,702; max_num_seqs blank 1,644; kv_quantization blank 1,247;
  prefix_caching blank 779. Frame (stop rule, warm-up, window, client release) never recorded.
- A blank is value_not_recorded (G5) unless the row matches a launcher preset (provisional rule) -> only matching
  rows score. M3.1 notes: 213 simulation-eligible train+validation units.
