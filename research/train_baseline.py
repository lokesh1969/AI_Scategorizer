"""
Classical baseline: TF-IDF (word 1-2 grams + character 2-5 grams) + Logistic Regression.
Character n-grams make the baseline robust to OCR noise and usable on Devanagari text.
C is chosen on the validation set (macro-F1); the test set is only predicted once.

    python research/train_baseline.py --data-dir research/data/splits --out research/results/tfidf_lr
"""
import argparse
import os
import time

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import FeatureUnion, Pipeline

from common import label_list, load_split, save_json, set_seed, write_predictions


def build(C: float, seed: int) -> Pipeline:
    features = FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, max_features=100000, sublinear_tf=True)),
    ])
    clf = LogisticRegression(C=C, max_iter=2000, class_weight="balanced", random_state=seed)
    return Pipeline([("features", features), ("clf", clf)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="research/data/splits")
    ap.add_argument("--out", default="research/results/tfidf_lr")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    set_seed(args.seed)

    train, val, test = (load_split(args.data_dir, s) for s in ("train", "val", "test"))
    labels = label_list(train)

    best = None
    for C in (0.5, 1.0, 4.0, 10.0):
        model = build(C, args.seed).fit(train["text"], train["label"])
        f1 = f1_score(val["label"], model.predict(val["text"]), average="macro")
        print(f"C={C:<5} val macro-F1={f1:.4f}")
        if best is None or f1 > best[1]:
            best = (C, f1, model)
    C, val_f1, model = best

    # Column order of predict_proba follows model.classes_ (sorted, same as `labels`)
    assert list(model.classes_) == labels
    start = time.perf_counter()
    test_probs = model.predict_proba(test["text"])
    ms_per_doc = (time.perf_counter() - start) * 1000 / max(1, len(test))

    write_predictions(os.path.join(args.out, "predictions_val.csv"), val, labels, model.predict_proba(val["text"]))
    write_predictions(os.path.join(args.out, "predictions_test.csv"), test, labels, test_probs)
    joblib.dump(model, os.path.join(args.out, "model.joblib"))
    save_json(os.path.join(args.out, "run_info.json"), {
        "model": "TF-IDF (word+char) + Logistic Regression",
        "best_C": C,
        "val_macro_f1": round(val_f1, 4),
        "labels": labels,
        "seed": args.seed,
        "inference_ms_per_doc_cpu": round(ms_per_doc, 3),
        "train_size": len(train),
    })
    print(f"Saved baseline (C={C}) to {args.out}")


if __name__ == "__main__":
    main()
