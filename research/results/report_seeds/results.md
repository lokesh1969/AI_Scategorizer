# Experiment results

Threshold target: auto-routed accuracy >= 95% (chosen on validation, reported on test).

## Main results (test set, 95% bootstrap CI)

| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |
|---|---|---|---|---|---|---|---|
| distilbert_s1 | 97.2 [94.4, 99.4] | 97.2 [94.5, 99.4] | 0.023 → 0.026 | 0.00 | 100.0 | 97.2 | 0.0011 |
| distilbert_s2 | 97.8 [95.6, 99.4] | 97.8 [95.3, 99.5] | 0.012 → 0.018 | 0.00 | 100.0 | 97.8 | 0.0010 |
| roberta_s1 | 98.3 [96.1, 100.0] | 98.3 [96.2, 100.0] | 0.015 → 0.018 | 0.00 | 100.0 | 98.3 | 0.0010 |
| roberta_s2 | 96.7 [93.9, 98.9] | 96.7 [93.8, 98.9] | 0.016 → 0.019 | 0.00 | 100.0 | 96.7 | 0.0022 |

## Paired McNemar tests (test)

| A | B | A right, B wrong | A wrong, B right | p-value |
|---|---|---|---|---|
| distilbert_s1 | distilbert_s2 | 1 | 2 | 1 |
| distilbert_s1 | roberta_s1 | 0 | 2 | 0.5 |
| distilbert_s1 | roberta_s2 | 1 | 0 | 1 |
| distilbert_s2 | roberta_s1 | 0 | 1 | 1 |
| distilbert_s2 | roberta_s2 | 2 | 0 | 0.5 |
| roberta_s1 | roberta_s2 | 3 | 0 | 0.25 |
