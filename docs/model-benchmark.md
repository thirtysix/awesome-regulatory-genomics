# Model benchmark

Generated 2026-07-25 by `pipeline/bench_models.py` on 75 sampled tools (25 hand-labelled).

A general intelligence ranking does not predict performance on a narrow structured-classification task, so the model is chosen by measurement. `agreement` is Jaccard overlap with the rule-derived categories — a sanity signal, not ground truth, since beating the rules is the point. `gold_F1` is scored against hand-labelled tools and is the number that matters.

| Model | JSON ok | Enum ok | Agreement | Gold F1 | $/100 tools | Median latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek-ai/DeepSeek-V4-Flash` | 100% | 100% | 0.52 | 0.83 | $0.004 | 1.3s |
| `deepseek-ai/DeepSeek-V3.1-Terminus` | 100% | 99% | 0.54 | 0.82 | $0.010 | 1.0s |
| `zai-org/GLM-5` | 100% | 100% | 0.53 | 0.85 | $0.015 | 1.4s |

Full catalog is 1626 tools, so multiply the per-100 cost by roughly 17 for a full pass.

### Failures — `deepseek-ai/DeepSeek-V3.1-Terminus` (1)

- Basset: bad enum ['chromatin-accessibility', 'tfbs-prediction']
