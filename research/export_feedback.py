"""
Exports documents reviewed in the app's Human Verification Queue as labelled data
and reports how often reviewers overrode the model. Use it to:
  * grow the training set with real, human-labelled documents (active learning loop), and
  * report live "human override rate" for the human-in-the-loop section of the paper.

    python research/export_feedback.py --out research/data/feedback.csv

Run from the project root (it reads the same database the API uses).
"""
import argparse
import os
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.db.database import db_adapter  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="research/data/feedback.csv")
    args = ap.parse_args()

    docs = db_adapter.get_documents()
    reviewed = [d for d in docs if d.get("verification_status") == "HUMAN VERIFIED" and d.get("verified_category")]

    rows = []
    for d in reviewed:
        c = d.get("classification", {})
        model_pred = c.get("model_prediction")
        rows.append({
            "id": d["_id"],
            "text": d.get("extracted_text", ""),
            "label": d["verified_category"],
            "language": d.get("language", "unknown"),
            "source": "human_verification",
            "model_prediction": model_pred,
            "model_confidence": c.get("model_confidence", c.get("confidence")),
            "model_name": c.get("model_name"),
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    df.to_csv(args.out, index=False, encoding="utf-8")

    status = Counter(d.get("verification_status") for d in docs)
    print(f"Documents: {len(docs)}  |  status counts: {dict(status)}")
    known = df[df["model_prediction"].notna()] if len(df) else df
    if len(known):
        agree = (known["model_prediction"] == known["label"]).mean()
        print(f"Human-reviewed with recorded model prediction: {len(known)}; model agreed with reviewer on {agree:.1%}")
    print(f"Wrote {len(df)} labelled rows to {args.out}")


if __name__ == "__main__":
    main()
