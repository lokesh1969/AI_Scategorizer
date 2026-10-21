"""
Builds research/data/dataset.csv automatically from public Hugging Face datasets.
Labels come from each source's own metadata (no manual labelling), and every
class mixes several sources so a model cannot classify by "which dataset is this".

    pip install datasets
    python research/build_dataset.py --per-class 300

| Label      | Sources (HF id)                                                                |
|------------|--------------------------------------------------------------------------------|
| FINANCE    | dvgodoy/rvl_cdip_mini (invoice, budget; real OCR), mychen76/invoices-and-receipts_ocr_v1 (synthetic invoices), Tobi-Bueck/customer-support-tickets (queue "Billing and Payments", synthetic) |
| HR         | Divyaamith/Kaggle-Resume (all job categories), rvl_cdip_mini (resume), support tickets (queue "Human Resources") |
| LEGAL      | coastalcph/lex_glue ledgar (contract clauses, SEC filings), coastalcph/lex_glue unfair_tos (terms-of-service clauses) |
| OPERATIONS | baker-street/maib-incident-reports-5K (marine incident reports), support tickets (technical/IT/outage queues) |

Check each source's licence before redistributing the generated CSV
(the support-ticket dataset is CC BY-NC 4.0: research use only).
"""
import argparse
import ast
import json
import os
import random
import re
from collections import Counter, defaultdict

import pandas as pd

from common import save_json

MAX_CHARS = 4000
MIN_CHARS = 80

TICKET_QUEUES = {
    "Billing and Payments": "FINANCE",
    "Human Resources": "HR",
    "Technical Support": "OPERATIONS",
    "IT Support": "OPERATIONS",
    "Service Outages and Maintenance": "OPERATIONS",
}
RVL_CATEGORIES = {"invoice": "FINANCE", "budget": "FINANCE", "resume": "HR"}

# Share of each class drawn from each source (normalised per class at sampling time)
MIX = {
    "FINANCE": {"rvl_cdip": 0.4, "invoices_ocr": 0.3, "support_tickets": 0.3},
    "HR": {"kaggle_resume": 0.4, "rvl_cdip": 0.3, "support_tickets": 0.3},
    "LEGAL": {"ledgar": 0.6, "unfair_tos": 0.4},
    "OPERATIONS": {"maib_incidents": 0.5, "support_tickets": 0.5},
}


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CHARS]


def take(iterable, n):
    out = []
    for item in iterable:
        out.append(item)
        if len(out) >= n:
            break
    return out


def load(name, config=None, split="train", streaming=True):
    from datasets import load_dataset
    return load_dataset(name, config, split=split, streaming=streaming)


def source_kaggle_resume(n):
    ds = load("Divyaamith/Kaggle-Resume")
    rows = ({"text": clean(r["Resume_str"]), "label": "HR", "detail": r["Category"]} for r in ds)
    return take((r for r in rows if len(r["text"]) >= MIN_CHARS), n)


def source_ledgar(n):
    ds = load("coastalcph/lex_glue", "ledgar")
    return take(({"text": clean(r["text"]), "label": "LEGAL", "detail": "contract clause"}
                 for r in ds if len(r["text"]) >= MIN_CHARS), n)


def source_unfair_tos(n):
    ds = load("coastalcph/lex_glue", "unfair_tos")
    return take(({"text": clean(r["text"]), "label": "LEGAL", "detail": "terms of service clause"}
                 for r in ds if len(r["text"]) >= MIN_CHARS), n)


def source_maib(n):
    ds = load("baker-street/maib-incident-reports-5K")
    return take(({"text": clean(r["text"]), "label": "OPERATIONS", "detail": r["label"]}
                 for r in ds if len(r["text"]) >= MIN_CHARS), n)


def source_tickets(per_label):
    """English tickets mapped by queue. per_label: {label: n}."""
    ds = load("Tobi-Bueck/customer-support-tickets")
    need = dict(per_label)
    out = []
    for r in ds:
        if r.get("language") != "en":
            continue
        label = TICKET_QUEUES.get(r.get("queue"))
        if not label or need.get(label, 0) <= 0:
            continue
        text = clean(f"{r.get('subject') or ''}. {r.get('body') or ''}")
        if len(text) < MIN_CHARS:
            continue
        out.append({"text": text, "label": label, "detail": r["queue"]})
        need[label] -= 1
        if all(v <= 0 for v in need.values()):
            break
    return out


def source_rvl(per_label):
    """RVL-CDIP mini: real scanned documents with OCR words (labels from the RVL category)."""
    need = dict(per_label)
    out = []
    for split in ("train", "validation", "test"):
        for r in load("dvgodoy/rvl_cdip_mini", split=split):
            label = RVL_CATEGORIES.get(r["category"])
            if not label or need.get(label, 0) <= 0:
                continue
            text = clean(" ".join(r["ocr_words"]))
            if len(text) < MIN_CHARS:
                continue
            out.append({"text": text, "label": label, "detail": f"rvl:{r['category']}"})
            need[label] -= 1
            if all(v <= 0 for v in need.values()):
                return out
    return out


def source_invoices_ocr(n):
    ds = load("mychen76/invoices-and-receipts_ocr_v1")
    out = []
    for r in ds:
        try:
            raw = json.loads(r["raw_data"]) if isinstance(r["raw_data"], str) else r["raw_data"]
            words = raw.get("ocr_words", [])
            words = ast.literal_eval(words) if isinstance(words, str) else words
        except (ValueError, SyntaxError, AttributeError):
            continue
        text = clean(" ".join(map(str, words)))
        if len(text) >= MIN_CHARS:
            out.append({"text": text, "label": "FINANCE", "detail": "invoice/receipt"})
        if len(out) >= n:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=300)
    ap.add_argument("--out", default="research/data/dataset.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    # How many rows each source must deliver per label
    quota = defaultdict(dict)
    for label, mix in MIX.items():
        total = sum(mix.values())
        for src, share in mix.items():
            quota[src][label] = round(args.per_class * share / total)
    # Over-fetch 30% so duplicates/short texts can be dropped and still fill the quota
    over = lambda n: int(n * 1.3) + 5

    fetchers = {
        "kaggle_resume": lambda q: source_kaggle_resume(over(q["HR"])),
        "ledgar": lambda q: source_ledgar(over(q["LEGAL"])),
        "unfair_tos": lambda q: source_unfair_tos(over(q["LEGAL"])),
        "maib_incidents": lambda q: source_maib(over(q["OPERATIONS"])),
        "support_tickets": lambda q: source_tickets({k: over(v) for k, v in q.items()}),
        "rvl_cdip": lambda q: source_rvl({k: over(v) for k, v in q.items()}),
        "invoices_ocr": lambda q: source_invoices_ocr(over(q["FINANCE"])),
    }
    synthetic = {"support_tickets", "invoices_ocr"}

    rows = []
    for src, q in quota.items():
        print(f"Fetching {src} for {q} ...", flush=True)
        try:
            fetched = fetchers[src](q)
        except Exception as e:  # keep going if one source is unavailable
            print(f"  ! {src} failed: {e}")
            continue
        by_label = defaultdict(list)
        for r in fetched:
            by_label[r["label"]].append(r)
        for label, n in q.items():
            pool = by_label[label]
            random.shuffle(pool)
            for r in pool[:n]:
                rows.append({**r, "language": "English", "source": src, "synthetic": src in synthetic})
            print(f"  {label:<11} got {min(n, len(pool))}/{n}")

    df = pd.DataFrame(rows)
    df = df.drop_duplicates("text").sample(frac=1, random_state=args.seed).reset_index(drop=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    df[["text", "label", "language", "source", "synthetic", "detail"]].to_csv(args.out, index=False, encoding="utf-8")

    card = {
        "rows": len(df),
        "per_label": df["label"].value_counts().to_dict(),
        "per_label_source": {f"{l} / {s}": int(c) for (l, s), c in Counter(zip(df["label"], df["source"])).items()},
        "synthetic_share": round(float(df["synthetic"].mean()), 3),
        "seed": args.seed,
    }
    save_json(os.path.splitext(args.out)[0] + "_card.json", card)
    print(json.dumps(card, indent=2))
    print(f"\nWrote {args.out}. Next: python research/split_dataset.py --input {args.out}")


if __name__ == "__main__":
    main()
