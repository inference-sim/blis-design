# Mistral-Large-4 and Inkling-2-Small: kinds of layer, and kernels with no GB200 measurement

Checked 2026-11-18. It backs requirements DC4. Sources:
- the Hugging Face configs: Inkling-2-Small's is public; Mistral-Large-4's is gated and returned HTTP 401 without
  an access token;
- vLLM's model code on main and at v0.34.0 (`vllm/models/inkling2/`, `vllm/models/mistral/`);
- blis-substrate `main`: `catalog/scripts/derive_graph.py`, `catalog/models/inkling/graph.yaml` and
  `registry/coefficients/*.yaml`.

## Inkling-2-Small (`Inkling2ForConditionalGeneration`, vLLM main `abb8194dc3`)

- **Close to Inkling (v1), which the catalog has.** v1 is built by the `InklingForConditionalGeneration` branch of
  the catalog's MoE handler. Its graph models sliding-window and full grouped-query attention plus MoE only. v1's
  relative-position attention (`d_rel`), short convolution and log scaling are not separate nodes.
- **New in v2:**
  - block attention residuals: fp32 pseudo-queries that mix earlier block outputs, in every layer;
  - no shared experts (v1 had 2);
  - NVFP4 experts, with MXFP8 on some layers;
  - softcaps on the MoE gate and up projections, and a final logit softcap of 30;
  - value normalisation, and clips on the q, k and relative-position projections;
  - an MTP drafter with a Markov head (`rnn_hidden`, block size 8), run as DSpark.
- **Graph vocabulary.** None is expected to be new at v1's level of detail. The attention residuals and the softcaps
  fit as elementwise nodes, and the drafter follows the catalog's other DSpark drafters. So the catalog work is a
  branch of the existing handler, and does not depend on the engine work.
- **Engine.** Its own kernels are in `vllm/models/inkling2/nvidia/ops`: `attention.py` (FA4 relative-position
  attention, `rel_decode_attention`), `moe.py` with `trtllm_bmm.cu` (a custom TRT-LLM batched GEMM, with its own
  routing and combine), `allreduce.py` (its own workspace), `seq_parallel.py`, `sconv.py`, `nvfp4.py` and `mxfp8.py`.
  blis-vllm must lower these, which is model support.
- **Coefficients on GB200.**
  - NVFP4 and MXFP8 grouped GEMMs have no entry on any Blackwell part: the `nvfp4_grouped` and `mxfp8` entries are
    on H100 and H200 only. The FP8 TRT-LLM grouped GEMM on GB200 is assumed.
  - Relative-position attention would be priced as plain grouped-query or sliding-window attention, which is
    measured on GB200. That is an approximation.
  - The launch cost on GB200 is the 3.2 µs derived from Hopper (blis-substrate#140).

## Mistral-Large-4 (`MistralLarge4ForCausalLM`, vLLM v0.34.0)

- **Structure.** Its module docstring says "MLA + DSA sparse attention, MoE, NoPE layers, KV sharing". Its
  `layer_spec.py` adds:
  - `kv_source_layer`: a layer attends to another layer's latent KV cache;
  - index sharing: a layer without an indexer reuses the top-k indices of the closest preceding indexer;
  - NoPE flags (layers without rotary position embedding), `ssmax` scaling, `first_k_dense_replace` and
    `moe_layer_freq`.
- **Graph vocabulary.** No new kind is expected. The DeepSeek-V4.1 handler already models `kv_source_layer_ids` and
  index sources, and GLM-5's handler models DSA. A new handler is needed. This is unconfirmed until the gated
  `config.json` is read.
- **Coefficients on GB200.**
  - Sparse-MLA attention has 31 entries, all on H100 and H200, none on any Blackwell part.
  - No entry is named for the indexer.
  - The MLA decode floor on GB200 is assumed.
  - The MoE precision is unknown until the config is read.
- **Drafter.** Its acceptance would be borrowed, unless a measured Mistral-Large-4 profile exists.
