"""Shared helpers for the research scripts: data loading, prediction files, seeding."""
import json
import os
import random
import sys
from typing import Dict, List

import numpy as np
import pandas as pd

# Windows consoles default to cp1252, which cannot print Hindi text or symbols like "→"
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_COLUMNS = ["text", "label"]
PROB_PREFIX = "prob_"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def load_split(data_dir: str, split: str) -> pd.DataFrame:
    """Loads train/val/test CSV written by split_dataset.py."""
    path = os.path.join(data_dir, f"{split}.csv")
    df = pd.read_csv(path, encoding="utf-8")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns {missing}")
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(str).str.strip().str.upper()
    if "language" not in df.columns:
        df["language"] = "unknown"
    if "id" not in df.columns:
        df["id"] = [f"{split}-{i}" for i in range(len(df))]
    return df


def label_list(train_df: pd.DataFrame) -> List[str]:
    return sorted(train_df["label"].unique().tolist())


def write_predictions(path: str, df: pd.DataFrame, labels: List[str], probs: np.ndarray) -> None:
    """
    Standard prediction file consumed by evaluate.py:
    id, text, language, label, pred, confidence, prob_<LABEL>...
    """
    out = pd.DataFrame({
        "id": df["id"].values,
        "text": df["text"].values,
        "language": df["language"].values,
        "label": df["label"].values,
    })
    pred_idx = probs.argmax(axis=1)
    out["pred"] = [labels[i] for i in pred_idx]
    out["confidence"] = probs.max(axis=1)
    for j, lab in enumerate(labels):
        out[f"{PROB_PREFIX}{lab}"] = probs[:, j]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.to_csv(path, index=False, encoding="utf-8")


def read_predictions(path: str):
    df = pd.read_csv(path, encoding="utf-8")
    prob_cols = [c for c in df.columns if c.startswith(PROB_PREFIX)]
    labels = [c[len(PROB_PREFIX):] for c in prob_cols]
    return df, labels, df[prob_cols].to_numpy(dtype=float)


def save_json(path: str, obj: Dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
