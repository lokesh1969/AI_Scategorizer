# Experiment results

Threshold target: auto-routed accuracy >= 95% (chosen on validation, reported on test).

## Main results (test set, 95% bootstrap CI)

| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |
|---|---|---|---|---|---|---|---|
| tfidf_lr | 98.3 [96.1, 100.0] | 98.3 [96.2, 100.0] | 0.251 → 0.014 | 0.00 | 100.0 | 98.3 | 0.0011 |
| distilbert_s42 | 98.3 [96.1, 100.0] | 98.3 [96.3, 100.0] | 0.015 → 0.015 | 0.00 | 100.0 | 98.3 | 0.0016 |
| roberta_s42 | 97.8 [95.6, 99.4] | 97.8 [95.4, 99.5] | 0.018 → 0.017 | 0.00 | 100.0 | 97.8 | 0.0021 |

## Paired McNemar tests (test)

| A | B | A right, B wrong | A wrong, B right | p-value |
|---|---|---|---|---|
| tfidf_lr | distilbert_s42 | 1 | 1 | 1 |
| tfidf_lr | roberta_s42 | 2 | 1 | 1 |
| distilbert_s42 | roberta_s42 | 2 | 1 | 1 |
