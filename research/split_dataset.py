"""
Creates ONE fixed train/val/test split that every model is trained and
evaluated on, so results are directly comparable and reproducible.

Input CSV columns: text, label (required); language, source, id (optional).
Labels must be one of FINANCE, HR, LEGAL, OPERATIONS (case-insensitive).

    python research/split_dataset.py --input research/data/dataset.csv --out research/data/splits

Exact-duplicate texts are removed before splitting so the same document can
never appear in both train and test (a common source of inflated scores).
"""
import argparse
import hashlib
import os

import pandas as pd
from sklearn.model_selection import train_test_split

from common import save_json

VALID_LABELS = {"FINANCE", "HR", "LEGAL", "OPERATIONS"}


def normalise(text: str) -> str:
    return " ".join(str(text).lower().split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="research/data/splits")
    ap.add_argument("--val-size", type=float, default=0.15)
    ap.add_argument("--test-size", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--holdout-source", default=None,
                    help="cross-source split: every row from this `source` becomes the test set and is "
                         "never seen in training (simulates a new kind of document arriving in deployment)")
    args = ap.parse_args()

    df = pd.read_csv(args.input, encoding="utf-8")
    df["label"] = df["label"].astype(str).str.strip().str.upper()
    df["text"] = df["text"].astype(str)
    if "language" not in df.columns:
        df["language"] = "unknown"

    bad = sorted(set(df["label"]) - VALID_LABELS)
    if bad:
        raise SystemExit(f"Unknown labels {bad}. Allowed: {sorted(VALID_LABELS)}")

    n_raw = len(df)
    df = df[df["text"].str.strip().str.len() > 0]
    df["_norm"] = df["text"].map(normalise)
    conflicting = df.groupby("_norm")["label"].nunique()
    conflicting = conflicting[conflicting > 1].index
    df = df[~df["_norm"].isin(conflicting)]  # same text with different labels = annotation error
    df = df.drop_duplicates("_norm").drop(columns="_norm").reset_index(drop=True)
    if "id" not in df.columns:
        df["id"] = [hashlib.sha1(t.encode("utf-8")).hexdigest()[:12] for t in df["text"]]

    # Stratify on label x language when every cell has enough rows, else on label only
    strat = df["label"] + "|" + df["language"].astype(str)
    if strat.value_counts().min() < 4:
        strat = df["label"]

    if args.holdout_source:
        if "source" not in df.columns or args.holdout_source not in set(df["source"]):
            raise SystemExit(f"--holdout-source '{args.holdout_source}' not found in the 'source' column")
        test = df[df["source"] == args.holdout_source]
        train_val = df[df["source"] != args.holdout_source]
        rel_val = args.val_size / (1 - args.test_size)
    else:
        train_val, test = train_test_split(df, test_size=args.test_size, stratify=strat, random_state=args.seed)
        rel_val = args.val_size / (1 - args.test_size)
    train, val = train_test_split(train_val, test_size=rel_val, stratify=strat.loc[train_val.index], random_state=args.seed)

    os.makedirs(args.out, exist_ok=True)
    for name, part in (("train", train), ("val", val), ("test", test)):
        part.to_csv(os.path.join(args.out, f"{name}.csv"), index=False, encoding="utf-8")

    info = {
        "input": os.path.abspath(args.input),
        "seed": args.seed,
        "holdout_source": args.holdout_source,
        "rows_raw": n_raw,
        "rows_after_dedup": len(df),
        "conflicting_texts_removed": int(len(conflicting)),
        "sizes": {"train": len(train), "val": len(val), "test": len(test)},
        "label_counts": {name: part["label"].value_counts().to_dict() for name, part in (("train", train), ("val", val), ("test", test))},
        "language_counts": {name: part["language"].value_counts().to_dict() for name, part in (("train", train), ("val", val), ("test", test))},
    }
    save_json(os.path.join(args.out, "split_info.json"), info)
    print(f"Wrote splits to {args.out}: {info['sizes']}")
    print(f"Removed {n_raw - len(df)} empty/duplicate/conflicting rows")


if __name__ == "__main__":
    main()
