# Experiment results

Threshold target: auto-routed accuracy >= 95% (chosen on validation, reported on test).

## Main results (test set, 95% bootstrap CI)

| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |
|---|---|---|---|---|---|---|---|
| tfidf_lr | 98.3 [96.1, 100.0] | 98.3 [96.2, 100.0] | 0.251 → 0.014 | 0.00 | 100.0 | 98.3 | 0.0011 |
| xsrc_support_tickets_tfidf_lr | 2.7 [1.2, 4.5] | 5.1 [2.2, 8.2] | 0.404 → 0.937 | 0.00 | 100.0 | 2.7 | 0.9972 |
| xsrc_rvl_cdip_tfidf_lr | 54.8 [47.6, 61.4] | 68.3 [62.5, 73.9] | 0.140 → 0.236 | 0.00 | 100.0 | 54.8 | 0.2748 |

## Paired McNemar tests (test)

| A | B | A right, B wrong | A wrong, B right | p-value |
|---|---|---|---|---|
| tfidf_lr | xsrc_support_tickets_tfidf_lr | - | - | different test sets |
| tfidf_lr | xsrc_rvl_cdip_tfidf_lr | - | - | different test sets |
| xsrc_support_tickets_tfidf_lr | xsrc_rvl_cdip_tfidf_lr | - | - | different test sets |
