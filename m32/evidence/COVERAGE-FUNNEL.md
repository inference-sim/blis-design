# Why few InferenceX and configiq units are scored

Checked 2026-11-18 and 2026-11-19. Sources:
- the accuracy-dashboard summary of the nightly `2026-11-18_blis-v0.18.0_ix-api-2026-11-18` (inference-sim v0.18.0,
  the M3.0 release);
- blis-substrate's ledger on `main` (`catalog/ledger/`);
- the InferenceX API, fetched 2026-11-18.

## InferenceX

**Table F1. 238 of 13,182 in-scope anchor units are scored; most of the rest are older than the age limit.**

| Stage | Units | Note |
|---|---|---|
| Units in the ledger | 82,347 | from db-dump/2026-09-28 and 16 supplement records |
| Anchor units (the dashboard's denominator) | 20,364 | the other roles are training data or held units |
| Anchor units on AMD parts, out of scope | 7,182 | no coefficients for AMD parts before M4 |
| Anchor units in scope | 13,182 | |
| Scored | 238 | all G4 |
| Not scored: older than the 180-day age limit | 11,555 | measured before 2026-05-23 |
| Not scored: inside the age limit, but the API no longer serves the row | 949 | a newer measurement of the configuration superseded it |
| Not scored: in the nightly's pull, refused for another reason | 440 | see Table F3 |

238 + 11,555 + 949 + 440 = 13,182. The dashboard records the second and third causes under one reason,
`value_not_recorded:not_in_pull_window`.

**Table F2. The in-scope anchor units the nightly did not pull, by engine family and measurement date.**

| Family | Before 2026-02 | 2026-02 to the age limit | Inside the age limit, superseded | Total |
|---|---|---|---|---|
| vLLM-family (vllm, dynamo-vllm, llmd-vllm, vllm-disagg) | 3,758 | 520 | 623 | 4,901 |
| SGLang-family (sglang, dynamo-sglang, mori-sglang) | 1,913 | 563 | 300 | 2,776 |
| TRT-LLM-family (trt, dynamo-trt) | 4,575 | 226 | 26 | 4,827 |
| Total | 10,246 | 1,309 | 949 | 12,504 |

The InferenceX API's `/server-log` was queried for 33 vLLM single-turn records that only the dump holds, three per
month. Every record from 2025-09 to 2026-01 returned 404; every record from 2026-02 to 2026-07 returned a log. So
the 3,758 vLLM-family units before 2026-02 have no server log on the API. Whether the dump holds their logs is not
checked. SGLang points take their launch command from the recipe at the run's commit, so the 1,913 older
SGLang-family units may still be recoverable.

**Table F3. The 440 in-scope anchor units the nightly pulled but did not score, by first reason.**

| First reason | Units |
|---|---|
| Dynamo's router has no entry in the router table (`router_unsupported`) | 252 |
| No SGLang field list in M3.0 (`field_unclassified`) | 96 |
| TRT-LLM has no engine (`engine_unsupported`) | 51 |
| Other: settings not modelled or not in the release, workload not stated, rows that differ from the ledger | 41 |

Counting every reason a unit carries, not only its first: 254 units are blocked by the router table, and 173 by the
missing SGLang field list (96 of them by nothing else). By family, the 440 are 173 SGLang-family, 156 vLLM-family
and 111 TRT-LLM-family.

**Rows published after the dump.** On 2026-11-18 the API served 1,216 in-scope rows dated after 2026-09-28 (AMD and
TPU parts excluded): 799 SGLang-family, 334 vLLM-family, 72 TRT-LLM-family and 11 others. The 1,133 vLLM- and
SGLang-family rows form about 1,090 distinct configurations at a concurrency, which approximates the units they
would make; 728 of the rows are single-node and not disaggregated. None is a ledger unit yet.

**Units in the ledger by framework.** vllm 40,941; trt 18,034; sglang 14,010; dynamo-trt 3,502; dynamo-sglang
2,404; atom 1,143; dynamo-vllm 1,036; mori-sglang 968; vllm-disagg 167; mooncake-atom 99; atom-disagg 20; llmd-vllm
12; tilert 11. Total 82,347.

## configiq

- The ledger holds 1,702 configiq units from dataset revision `21cc6eb`: 1,031 on H200, 226 on B200, 417 on MI355X
  and 28 on MI300X. AMD parts are out of scope, leaving 1,257.
- 328 role keys cover the 1,702 units, so a share drawn per role key applies only approximately to units.
- Every unit's `chunked_prefill_enabled` is blank, 1,644 have a blank `max_num_seqs`, 1,247 a blank
  `kv_quantization` and 779 a blank `prefix_caching`. The run's frame (stop rule, warm-up, measurement duration,
  client version) is never recorded.
- Today a blank counts as "not recorded" unless the row matches a forge preset. In M3.1, 213 of configiq's training
  and validation units could be simulated on that basis.
- configiq's units are not in the published anchor and fit lists on blis-substrate `main`.
