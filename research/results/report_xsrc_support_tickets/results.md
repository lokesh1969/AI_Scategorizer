# Experiment results

Threshold target: auto-routed accuracy >= 95% (chosen on validation, reported on test).

## Main results (test set, 95% bootstrap CI)

| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |
|---|---|---|---|---|---|---|---|
| xsrc_support_tickets_tfidf_lr | 2.7 [1.2, 4.5] | 5.1 [2.2, 8.2] | 0.404 → 0.937 | 0.00 | 100.0 | 2.7 | 0.9972 |
| xsrc_support_tickets_distilbert | 4.5 [2.4, 6.7] | 7.0 [3.8, 10.3] | 0.811 → 0.953 | 0.00 | 100.0 | 4.5 | 0.9950 |
| xsrc_support_tickets_roberta | 37.9 [32.7, 42.7] | 32.6 [28.4, 36.8] | 0.514 → 0.615 | 0.00 | 100.0 | 37.9 | 0.5566 |

## Paired McNemar tests (test)

| A | B | A right, B wrong | A wrong, B right | p-value |
|---|---|---|---|---|
| xsrc_support_tickets_tfidf_lr | xsrc_support_tickets_distilbert | 9 | 15 | 0.3075 |
| xsrc_support_tickets_tfidf_lr | xsrc_support_tickets_roberta | 4 | 120 | 9.121e-31 |
| xsrc_support_tickets_distilbert | xsrc_support_tickets_roberta | 0 | 110 | 1.541e-33 |
