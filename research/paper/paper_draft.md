# Random Splits Hide What Matters: Cross-Source Evaluation of Confidence-Based Human-in-the-Loop Routing for Enterprise Documents

> **Status of this draft.** Every number comes from `research/results/` (Colab T4 run plus the local baseline), so you can trace each one to a file.
> Before submitting, fill in the ✍️ items (author block, institution, GitHub link), check each reference on Google Scholar, and move the text into the IEEE conference template on Overleaf.
> Figures to include are listed in §VI.

✍️ *Authors, affiliation, email*

---

## Abstract

Document routing systems, which send each incoming document to the department that
must act on it, are usually evaluated on random train/test splits. We show that such
splits can hide exactly the differences that matter in deployment. We present **AI
Scategorizer**, an end-to-end system combining OCR, transformer classification into
Finance, HR, Legal and Operations, confidence-thresholded auto-routing, and a
role-based human verification queue.

We evaluate it on a 1,199-document benchmark built from seven public corpora. On a
random split, a TF-IDF baseline, DistilBERT and RoBERTa are statistically
indistinguishable, at 97.6–98.3% accuracy (McNemar *p* = 1.0). When an entire source is
held out:
- on unseen scanned documents, accuracy is 54.8% (TF-IDF), 78.6% (DistilBERT) and 92.9% (RoBERTa);
- on unseen support tickets, accuracy is 2.7%, 4.5% and 37.9% respectively.

RoBERTa's advantage over TF-IDF is highly significant on both held-out sources (McNemar *p* ≤ 1.1·10⁻¹⁸). Confidence thresholds behave just as
differently. On unseen scans, RoBERTa auto-routes 83.8% of documents at a 0.90
threshold with no errors. On unseen tickets, every model remains confidently wrong:
at the same threshold, each still auto-routes at least 89% of them. Thresholds selected on in-distribution validation
data were uninformative in all settings. We argue that leave-one-source-out evaluation
and human-override monitoring should be standard practice for document routing.

**Keywords:** document classification, distribution shift, cross-source evaluation, selective classification, calibration, human-in-the-loop, transformers

---

## I. Introduction

✍️ *Add one or two sentences of motivation from your own context (e.g. how documents are sorted in your institution or a partner organisation).*

Routing incoming documents to the department that must act on them is routine but
error-sensitive. A misrouted legal notice can miss a deadline, and a misrouted invoice
delays payment. Text classifiers based on TF-IDF features [1] or pre-trained
transformers [2] commonly report accuracies above 95% on random splits. Deployed
systems, however, keep meeting document *sources* absent from training: a new vendor's
invoice template, a new ticketing tool, a different scanner. If a model has learned the
surface style of its training sources rather than their content, random-split accuracy
says little about deployment.

A common safeguard is **selective routing** [3], [4]: a document is auto-routed only
when model confidence exceeds a threshold, and deferred to a human otherwise. This
relies on confidence staying informative under shift. Calibration methods such as
temperature scaling [5] are fitted on validation data that usually shares the training
distribution.

We ask:
- **RQ1:** Does a random split separate classical and transformer models on a department-routing task?
- **RQ2:** How do these models degrade when an entire document source is unseen?
- **RQ3:** Do confidence thresholds, as chosen in practice, still protect against misrouting under such shift?

**Contributions.**
1. **System.** An open, end-to-end document routing system: ingestion, OCR with image preprocessing, transformer classification, threshold routing, and a role-based verification queue that preserves the model's original prediction for auditing.
2. **Benchmark and protocol.** A reproducible four-class benchmark of 1,199 documents from seven public corpora, with a random-split protocol and two leave-one-source-out protocols.
3. **Findings.**
   - Three models that are indistinguishable on the random split differ by up to 38 accuracy points on unseen sources, and RoBERTa generalises best.
   - Confidence-based deferral works well for RoBERTa under OCR shift but fails for all models under a change of writing style.
   - In-distribution threshold selection never deferred a single document.

---

## II. Related Work

**Document classification.** Linear models on bag-of-words or TF-IDF features remain strong baselines [1]. Pre-trained transformers such as BERT [2], DistilBERT [6] and RoBERTa [7] are the current standard. For scanned documents, RVL-CDIP [8] and layout-aware models such as LayoutLM [9] are widely used, but RVL-CDIP labels document *types*, not the department that must act. Legal-domain benchmarks include LexGLUE [10], LEDGAR [11] and UNFAIR-ToS [12].

**Calibration and selective classification.** Modern neural networks are often mis-calibrated, and temperature scaling is a simple, strong fix [5]. Expected calibration error (ECE) [13] is the usual metric. Selective classification [3] abstains on low-confidence inputs, and maximum softmax probability is a common confidence score [4].

**Human-in-the-loop systems.** Learning-to-defer methods [14] and human-in-the-loop machine learning more broadly [15] study when to hand decisions to people. Our system records each reviewer's decision next to the model's prediction, which supports both auditing and retraining.

✍️ *Optional: add 1–2 citations on distribution shift / domain generalisation in NLP, or on document automation in Indian e-governance.*

---

## III. System Design

*Figure 1: system architecture. Redraw the Mermaid diagram from PROJECT.md §2.*

An uploaded file (PDF, DOCX, XLSX, TXT or image, up to 25 MB) goes through these steps:
1. **Text extraction.** Digital text is read directly. PDFs with almost no embedded text are treated as scans.
2. **OCR.** Pages are rendered at 300 DPI and preprocessed (grayscale, CLAHE contrast enhancement, median denoising, unsharp masking, deskewing, Otsu binarisation), then recognised with Tesseract [16].
3. **Normalisation and language identification.**
4. **Classification** by a fine-tuned transformer, which outputs a probability for each department.
5. **Rule-based enrichment** shown to reviewers: priority score, extractive summary, regex entities, lexicon sentiment.
6. **Routing.** With confidence *c* = max *p* and threshold τ, a document is auto-routed when *c* ≥ τ and deferred to the human verification queue otherwise. Empty or unreadable documents are always deferred.

Department reviewers see the extracted text, class probabilities and the preprocessed scan. Their decision re-routes the document, while the model's original prediction is kept (`model_prediction`, `human_override`). This yields a live **override rate**, which is the monitoring signal Section VII recommends. Access control is enforced on the server, and all actions are audit-logged.

**Implementation.** FastAPI backend, React frontend, MongoDB with an SQLite fallback, Hugging Face Transformers. Batched GPU inference took 1.7 ms per document for DistilBERT (67.0M parameters) and 3.8 ms for RoBERTa (124.6M) on an NVIDIA T4. The TF-IDF model took 2.0 ms per document on CPU.

---

## IV. Dataset

The benchmark was built automatically (`research/build_dataset.py`). Labels come from each source's own metadata.

**Table I: Dataset composition (1,199 documents, all English)**

| Class | Source | Docs | Type |
|---|---|---|---|
| FINANCE | RVL-CDIP invoices & budgets (scanned, OCR) [8] | 120 | real |
| | Invoice/receipt OCR (`mychen76/invoices-and-receipts_ocr_v1`) | 90 | synthetic |
| | Support tickets, *Billing and Payments* queue (`Tobi-Bueck/customer-support-tickets`) | 90 | synthetic |
| HR | Resumes, LiveCareer via Kaggle (`Divyaamith/Kaggle-Resume`) | 120 | real |
| | RVL-CDIP resumes (scanned, OCR) | 90 | real |
| | Support tickets, *Human Resources* queue | 90 | synthetic |
| LEGAL | LEDGAR contract provisions [11] | 180 | real |
| | UNFAIR-ToS clauses [12] | 119 | real |
| OPERATIONS | UK MAIB marine incident reports (`baker-street/maib-incident-reports-5K`) | 150 | real |
| | Support tickets, technical/IT/outage queues | 150 | synthetic |

Texts were whitespace-normalised and truncated to 4,000 characters. Texts shorter than 80 characters and exact duplicates were removed. Overall, 35% of documents are synthetic.

**Protocols.**
- **(a) Random split:** stratified 70/15/15 with seed 42, giving 839 / 180 / 180 documents.
- **(b) Leave-one-source-out:** every document from one source becomes the test set, and the remaining documents are split 85/15 into train and validation. We hold out:
  - *support tickets*: n = 330, covering FINANCE, HR and OPERATIONS;
  - *RVL-CDIP*: n = 210 noisy OCR scans, covering FINANCE and HR.

  Macro-F1 averages over the classes present in each test set, but predictions of any class, including absent ones, count as errors.

---

## V. Experimental Setup

**Models.**
1. **TF-IDF + LR:** word 1–2-grams plus character 2–5-grams, class-balanced logistic regression, with *C* ∈ {0.5, 1, 4, 10} chosen on validation macro-F1.
2. **DistilBERT-base-uncased** [6].
3. **RoBERTa-base** [7].

Transformers were fine-tuned on an NVIDIA T4 (Google Colab) for up to 5 epochs: learning rate 3·10⁻⁵, batch size 16, maximum 256 tokens, 10% linear warm-up, weight decay 0.01, keeping the epoch with the best validation macro-F1 and early stopping with patience 2. Random-split runs used seeds {42, 1, 2} and are reported as mean ± std. Cross-source runs used seed 42.

**Metrics.**
- Accuracy and macro-F1 with 95% bootstrap confidence intervals (1,000 resamples).
- ECE (15 bins) [13] before and after temperature scaling, with the temperature fitted on validation [5].
- Selective routing: coverage (share auto-routed), selective accuracy (accuracy of auto-routed documents) and AURC [3].
- The routing threshold τ was selected as the smallest value whose **validation** selective accuracy is at least 95%. We also report fixed operating points τ ∈ {0.80, 0.90, 0.95} from the test-set sweep for analysis.
- Paired McNemar tests [17] compare models on identical test documents.

---

## VI. Results

**Table II: Random split (test, n = 180). Transformers: mean ± std over 3 seeds**

| Model | Accuracy % | Macro-F1 % | ECE before → after | AURC |
|---|---|---|---|---|
| TF-IDF + LR | 98.3 [96.1, 100.0]† | 98.3 [96.2, 100.0]† | 0.251 → 0.014 | 0.0011 |
| DistilBERT | 97.8 ± 0.6 | 97.8 ± 0.6 | 0.017 → 0.020 | 0.0012 |
| RoBERTa | 97.6 ± 0.9 | 97.6 ± 0.9 | 0.016 → 0.018 | 0.0018 |

† 95% bootstrap CI (the baseline is deterministic). Seed-42 McNemar tests: all pairs *p* = 1.0.

**Table III: Leave-one-source-out (test = an unseen source; seed 42; 95% bootstrap CI)**

| Held-out source | Model | Accuracy % | Macro-F1 % | ECE before → after | AURC |
|---|---|---|---|---|---|
| Support tickets (n = 330) | TF-IDF + LR | 2.7 [1.2, 4.5] | 5.1 [2.2, 8.2] | 0.404 → 0.937 | 0.997 |
| | DistilBERT | 4.5 [2.4, 6.7] | 7.0 [3.8, 10.3] | 0.811 → 0.953 | 0.995 |
| | RoBERTa | **37.9** [32.7, 42.7] | **32.6** [28.4, 36.8] | 0.514 → 0.615 | **0.557** |
| RVL-CDIP scans (n = 210) | TF-IDF + LR | 54.8 [47.6, 61.4] | 68.3 [62.5, 73.9] | 0.140 → 0.236 | 0.275 |
| | DistilBERT | 78.6 [73.3, 83.3] | 80.8 [75.6, 85.4] | 0.099 → 0.070 | 0.074 |
| | RoBERTa | **92.9** [89.0, 96.2] | **92.8** [89.1, 96.1] | 0.053 → 0.049 | **0.006** |

McNemar tests:
- Support tickets: RoBERTa vs TF-IDF *p* = 9.1·10⁻³¹; RoBERTa vs DistilBERT *p* = 1.5·10⁻³³; DistilBERT vs TF-IDF *p* = 0.31.
- RVL-CDIP: DistilBERT vs TF-IDF *p* = 1.0·10⁻¹¹; RoBERTa vs TF-IDF *p* = 1.1·10⁻¹⁸; RoBERTa vs DistilBERT *p* = 1.5·10⁻⁵.

**Table IV: Selective routing on unseen sources (fixed thresholds)**

| Held-out source | Model | τ = 0.80: auto % / acc. % | τ = 0.90: auto % / acc. % | τ = 0.95: auto % / acc. % |
|---|---|---|---|---|
| Support tickets | TF-IDF + LR | 92.7 / 1.6 | 89.4 / 0.7 | 87.0 / 0.3 |
| | DistilBERT | 99.1 / 4.3 | 98.8 / 4.3 | 98.2 / 4.3 |
| | RoBERTa | 98.5 / 37.9 | 96.7 / 38.6 | 96.7 / 38.6 |
| RVL-CDIP scans | TF-IDF + LR | 55.2 / 67.2 | 36.7 / 80.5 | 21.9 / 84.8 |
| | DistilBERT | 66.7 / 91.4 | 54.3 / 93.0 | 41.0 / 96.5 |
| | RoBERTa | 91.4 / 96.4 | **83.8 / 100.0** | 68.6 / 100.0 |

### A. RQ1: The random split cannot separate the models

All three models reach 97.6–98.3% accuracy, with overlapping confidence intervals and McNemar *p* = 1.0 for every pair. The seed-42 models disagree on at most three of 180 test documents. Errors are mostly FINANCE documents predicted as HR (two or three per model), plus at most two documents sent to OPERATIONS. LEGAL is classified perfectly by all models. On this protocol, a linear baseline with at most 150k TF-IDF features is as good as a 124.6M-parameter transformer.

### B. RQ2: Unseen sources reveal large, significant differences

**Unseen OCR scans (RVL-CDIP).** RoBERTa keeps 92.9% accuracy, against 78.6% for DistilBERT and 54.8% for TF-IDF. The baseline sends 72 of 120 unseen scanned finance documents to LEGAL. DistilBERT confuses them mostly with HR (30) and OPERATIONS (12). RoBERTa misroutes only 4 FINANCE and 11 HR documents.

**Unseen support tickets.** All models degrade sharply, but RoBERTa is the only one well above chance: 37.9% accuracy, with OPERATIONS tickets recognised in 104 of 150 cases (F1 = 0.67). Billing tickets are never classified as FINANCE by any model. TF-IDF sends 88 of 90 to LEGAL, DistilBERT 90 of 90, and RoBERTa 69 of 90. In the training data, FINANCE consists of invoices and scanned budgets, so short conversational complaints about payments were never shown as financial. The models fall back on the closest *style*, the clause-like LEGAL text, rather than the *topic*.

### C. RQ3: Confidence protects under OCR shift, but not under style shift

Thresholds selected on validation data were **0.00 for every run**: in-distribution validation accuracy exceeded 95% at every threshold, so the procedure never deferred a document. Fixed thresholds tell a more nuanced story (Table IV).
- **On unseen scans,** RoBERTa's confidence is highly informative (AURC = 0.006). At τ = 0.90 it auto-routes 83.8% of documents with **no errors** and defers the remaining 16.2% to reviewers. The weaker models need far more deferral for lower accuracy: TF-IDF auto-routes only 36.7% at 80.5% accuracy.
- **On unseen tickets,** confidence is uninformative for every model. Even at τ = 0.95, 87–98% of tickets are auto-routed, and at most 38.6% of those are correct.

Temperature scaling barely changed in-distribution calibration for the transformers, whose ECE was already below 0.02. For the TF-IDF baseline it reduced ECE from 0.251 to 0.014. Under shift, it *increased* ECE in four of six cases, most sharply on the tickets: 0.404 → 0.937 for TF-IDF and 0.811 → 0.953 for DistilBERT. Temperatures fitted on easy, in-distribution validation data (T < 1) sharpen predictions and make confidently wrong outputs even more confident.

*Figures (in `research/paper/figures/`):*
- *Fig. 2: Coverage and selective accuracy vs threshold for RoBERTa on unseen scans (`fig2a_threshold_rvl_roberta.png`) and unseen tickets (`fig2b_threshold_tickets_roberta.png`).*
- *Fig. 3: Confusion matrix of TF-IDF on unseen support tickets; most tickets are predicted as LEGAL (`fig3_confusion_tickets_tfidf.png`).*
- *Fig. 4: Reliability diagram for RoBERTa on unseen scans, before and after temperature scaling (`fig4_reliability_rvl_roberta.png`).*

---

## VII. Discussion

- **Report leave-one-source-out results.** A random split mixed documents of the same template and style into training and test, and made a linear TF-IDF model look equivalent to RoBERTa. One held-out source was enough to reveal a 38-point gap.
- **Pre-training helps, but has limits.** RoBERTa's advantage is consistent with broader pre-training giving more topic-level, less style-level representations. However, no model learned that a billing complaint is a finance matter when every finance training example was an invoice. Training data should cover each department's *genres*, not just its topics.
- **Calibrate and choose thresholds on deployment-like data.** In-distribution validation never deferred anything, and in-distribution temperatures worsened calibration under shift. A small, recent sample of real incoming documents is a better basis for both.
- **Monitor overrides.** Because the verification queue stores `model_prediction` and `human_override`, a rising override rate, or a falling deferral rate while complaints increase, is a practical alarm for the kind of style shift that confidence alone cannot detect.

**Limitations.**
- The benchmark is small (1,199 documents), English-only and 35% synthetic.
- LEGAL is drawn only from clause corpora.
- Cross-source results use one seed, and only two sources were held out.
- The models read at most 256 tokens.
- The fixed-threshold analysis (Table IV) reads operating points from the test sweep. It characterises behaviour and is not a tuned result.

---

## VIII. Conclusion

On a random split, a TF-IDF baseline, DistilBERT and RoBERTa were indistinguishable at
about 98% accuracy. Holding out a single document source revealed accuracies of 2.7%
to 92.9% and significant differences between the models. Confidence thresholding was
highly effective for RoBERTa under OCR shift (83.8% automated with no errors) and
ineffective for every model under a change of writing style. Cross-source evaluation,
threshold selection on deployment-like data and human-override monitoring should
accompany any claim that document routing is ready for automation.

**Future work:**
- bilingual Hindi–English documents with Indic encoders [18], [19];
- layout-aware models for scans;
- out-of-distribution detection alongside confidence thresholds;
- retraining from reviewer corrections.

**Data and code availability.** Dataset construction, splits, training and evaluation code: ✍️ *GitHub link*. The source corpora are public on Hugging Face under their own licences; the support-ticket corpus is CC BY-NC 4.0.

---

## References

[1] T. Joachims, "Text categorization with support vector machines: Learning with many relevant features," in *Proc. ECML*, 1998.
[2] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," in *Proc. NAACL-HLT*, 2019.
[3] Y. Geifman and R. El-Yaniv, "Selective classification for deep neural networks," in *Proc. NeurIPS*, 2017.
[4] D. Hendrycks and K. Gimpel, "A baseline for detecting misclassified and out-of-distribution examples in neural networks," in *Proc. ICLR*, 2017.
[5] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *Proc. ICML*, 2017.
[6] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter," arXiv:1910.01108, 2019.
[7] Y. Liu *et al.*, "RoBERTa: A robustly optimized BERT pretraining approach," arXiv:1907.11692, 2019.
[8] A. W. Harley, A. Ufkes, and K. G. Derpanis, "Evaluation of deep convolutional nets for document image classification and retrieval," in *Proc. ICDAR*, 2015.
[9] Y. Xu *et al.*, "LayoutLM: Pre-training of text and layout for document image understanding," in *Proc. KDD*, 2020.
[10] I. Chalkidis *et al.*, "LexGLUE: A benchmark dataset for legal language understanding in English," in *Proc. ACL*, 2022.
[11] D. Tuggener, P. von Däniken, T. Peetz, and M. Cieliebak, "LEDGAR: A large-scale multi-label corpus for text classification of legal provisions in contracts," in *Proc. LREC*, 2020.
[12] M. Lippi *et al.*, "CLAUDETTE: An automated detector of potentially unfair clauses in online terms of service," *Artificial Intelligence and Law*, 2019.
[13] M. P. Naeini, G. F. Cooper, and M. Hauskrecht, "Obtaining well calibrated probabilities using Bayesian binning," in *Proc. AAAI*, 2015.
[14] H. Mozannar and D. Sontag, "Consistent estimators for learning to defer to an expert," in *Proc. ICML*, 2020.
[15] X. Wu *et al.*, "A survey of human-in-the-loop for machine learning," *Future Generation Computer Systems*, 2022.
[16] R. Smith, "An overview of the Tesseract OCR engine," in *Proc. ICDAR*, 2007.
[17] T. G. Dietterich, "Approximate statistical tests for comparing supervised classification learning algorithms," *Neural Computation*, 1998.
[18] S. Khanuja *et al.*, "MuRIL: Multilingual representations for Indian languages," arXiv:2103.10730, 2021.
[19] A. Conneau *et al.*, "Unsupervised cross-lingual representation learning at scale," in *Proc. ACL*, 2020.

Dataset sources to cite in a footnote or data-availability statement: the Hugging Face IDs listed in `research/build_dataset.py`. ✍️ *Check every reference against Google Scholar before submitting. Page numbers and author lists must be exact.*
