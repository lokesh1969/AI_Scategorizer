# Experiment results

Threshold target: auto-routed accuracy >= 95% (chosen on validation, reported on test).

## Main results (test set, 95% bootstrap CI)

| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |
|---|---|---|---|---|---|---|---|
| xsrc_rvl_cdip_tfidf_lr | 54.8 [47.6, 61.4] | 68.3 [62.5, 73.9] | 0.140 → 0.236 | 0.00 | 100.0 | 54.8 | 0.2748 |
| xsrc_rvl_cdip_distilbert | 78.6 [73.3, 83.3] | 80.8 [75.6, 85.4] | 0.099 → 0.070 | 0.00 | 100.0 | 78.6 | 0.0743 |
| xsrc_rvl_cdip_roberta | 92.9 [89.0, 96.2] | 92.8 [89.1, 96.1] | 0.053 → 0.049 | 0.00 | 100.0 | 92.9 | 0.0061 |

## Paired McNemar tests (test)

| A | B | A right, B wrong | A wrong, B right | p-value |
|---|---|---|---|---|
| xsrc_rvl_cdip_tfidf_lr | xsrc_rvl_cdip_distilbert | 5 | 55 | 1.038e-11 |
| xsrc_rvl_cdip_tfidf_lr | xsrc_rvl_cdip_roberta | 7 | 87 | 1.122e-18 |
| xsrc_rvl_cdip_distilbert | xsrc_rvl_cdip_roberta | 9 | 39 | 1.522e-05 |
