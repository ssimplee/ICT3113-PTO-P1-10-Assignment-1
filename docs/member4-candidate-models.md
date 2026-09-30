# Member 4 candidate-model selection

## Decision status

This is the tested shortlist proposed for team approval. It is not yet the
frozen prediction record. Full local digests and synthetic compatibility
evidence are recorded in `docs/member4-model-manifest.json`.

## Constraints used

- CPU-only inference; no public model API.
- Four candidates, spanning sub-1B, 1-2B and 3B size bands.
- Explicit instruction-tuned Q4 tags to keep the comparison reproducible and
  feasible within the observed 4.0 GB Docker allocation on an 8 GB host.
- Text-only classification with deterministic temperature zero and an Ollama
  JSON schema supplied by the existing service.
- At least one cross-family candidate so the exercise is not only a Qwen size
  comparison.

## Proposed shortlist

| Exact Ollama tag | Full local digest (`sha256:`) | Download size | Role in comparison | Licence |
|---|---|---:|---|---|
| `qwen3:0.6b-q4_K_M` | `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435` | 523 MB | Qwen lower bound | Apache 2.0 |
| `llama3.2:1b-instruct-q4_K_M` | `22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02` | 808 MB | Llama lower bound and cross-family control | Llama 3.2 Community License |
| `qwen3:1.7b-q4_K_M` | `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7` | 1.36 GB | Larger Qwen scaling point | Apache 2.0 |
| `llama3.2:3b-instruct-q4_K_M` | `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72` | 2.02 GB | Larger Llama scaling point and upper practical tier | Llama 3.2 Community License |

These tags and sizes are documented in the official Ollama registries:

- https://ollama.com/library/qwen3/tags
- https://ollama.com/library/llama3.2/tags

Qwen states that its open-weight Qwen3 models use Apache 2.0:
https://github.com/QwenLM/Qwen3. Meta publishes Llama 3.2 under its Community
License: https://dev.meta.ai/llama/llama3_2/license. Both licences must be
acknowledged on the final references slide.

## Why these four

The design now supports two within-family scaling comparisons (Qwen 0.6B to
1.7B and Llama 1B to 3B) plus cross-family comparisons. This is more balanced
than treating one Llama model as a single control. Q4_K_M is used throughout to
avoid comparing different quantisation levels as if parameter count were the
only difference.

An 8B model was rejected without pulling because its Q4 artifact alone is about
5.2 GB. The initially proposed `qwen3:4b-instruct-2507-q4_K_M` was pulled and did
load at 3.2 GB, but both cold and warm synthetic requests exceeded the service's
120-second Ollama timeout. It returned HTTP 504 after 121.309 and 120.931 seconds,
respectively. It was therefore replaced before formal testing rather than
silently changing the prompt or timeout for one candidate. The full rejected
model digest and both request IDs remain in the manifest.

## Completed compatibility gate

All four shortlisted models returned HTTP 201 through the real `/tickets`
service, reported their intended exact tag, produced a supported one-key
category result and were observed at `100% CPU`. Their one-off cold diagnostic
times were 42.117, 25.995, 51.826 and 81.564 seconds in the table order above.
These figures establish compatibility only: they are not accuracy, latency or
load benchmark results, and the returned categories were not scored.

## Pinning procedure

The exact tags have been pulled and their full digests captured from Ollama's
local `/api/tags` response. The manifest also records sizes, Ollama image and
runtime versions, Docker resources, Git revision and capture timestamp.

The compatibility checks used only an explicitly synthetic complaint. No golden
narrative was submitted. Formal testing remains blocked until the independent
human labels and prediction freeze are complete.
