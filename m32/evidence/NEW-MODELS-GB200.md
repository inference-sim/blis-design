# Mistral-Large-4 and Inkling-2-Small: new layers and unmeasured kernels (checked 2026-11-18)

Sources: HF config (Inkling-2-Small public; Mistral-Large-4 gated, 401 without a token), vLLM main and v0.34.0
model code (vllm/models/inkling2/, vllm/models/mistral/), blis-substrate origin/main catalog/scripts/derive_graph.py,
catalog/models/inkling/graph.yaml, registry/coefficients/*.yaml.

## Inkling-2-Small (Inkling2ForConditionalGeneration, vLLM main abb8194dc3)
- Close to Inkling v1, which the catalog has (handler_moe branch for InklingForConditionalGeneration). v1's graph
  models SWA and full GQA attention plus MoE only: its relative-position attention (d_rel), short conv and log
  scaling are not separate nodes.
- New in v2: block attention residuals (attn_res: fp32 pseudo-query mixing of block outputs, every layer);
  no shared experts (v1 had 2); NVFP4 experts (MXFP8 on some layers); MoE gate/up softcaps; final logit
  softcap 30; value norm and qk/rel clips; MTP/DSpark drafter with a Markov head (rnn_hidden, block_size 8).
- Vocabulary: none needed at v1's fidelity. attn_res and the softcaps fit as Elementwise nodes; the drafter
  follows the DSpark drafters the catalog already has. So catalog work is a handler branch, independent of
  the engine move.
- Engine: custom kernels in vllm/models/inkling2/nvidia/ops: attention.py (FA4 relative attention,
  rel_decode_attention), moe.py + trtllm_bmm.cu (custom TRT-LLM batched GEMM, own route/combine),
  allreduce.py (own workspace), seq_parallel.py, sconv.py, nvfp4.py, mxfp8.py.
- GB200 coefficients: no NVFP4 or MXFP8 grouped-GEMM entry for any Blackwell part (nvfp4_grouped: h100, h200 only;
  mxfp8: h100, h200); fp8 TRT-LLM grouped on GB200 is assumed. Relative attention would be priced as plain
  GQA/SWA (measured on GB200), an approximation. Launch cost on GB200 is the Hopper-derived 3.2 us
  (blis-substrate#140).

## Mistral-Large-4 (MistralLarge4ForCausalLM, vLLM v0.34.0)
- Docstring: "MLA + DSA sparse attention, MoE, NoPE layers, KV sharing". layer_spec.py: kv_source_layer (a layer
  attends to another layer's latent KV), index sharing (layers without an indexer reuse the closest preceding
  indexer's top-k), NoPE flags, ssmax scaling, first_k_dense_replace and moe_layer_freq.
- Vocabulary: no new kind expected. The DeepSeek-V4.1 handler already models kv_source_layer_ids and index
  sources; GLM-5's handler models DSA. A new handler is needed. Unconfirmed until the gated config.json is read.
- GB200 coefficients: sparse-MLA attention has 31 entries, all h100/h200, none on any Blackwell part; no
  indexer entry by name; MLA decode floor on GB200 is assumed. MoE precision unknown until the config is read.
  DSpark drafter: acceptance would be borrowed unless a measured Mistral-Large-4 profile exists.
