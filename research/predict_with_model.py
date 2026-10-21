"""
Produces evaluate.py-compatible predictions for an already trained Hugging Face
model directory (for example the model the app currently serves), without retraining.

    python research/predict_with_model.py --model-dir models/classifier --data-dir research/data/splits --out research/results/deployed
"""
import argparse
import os

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from common import load_split, save_json, write_predictions


def predict(model, tokenizer, texts, max_length, batch_size=32):
    probs = []
    for i in range(0, len(texts), batch_size):
        enc = tokenizer(texts[i:i + batch_size], truncation=True, max_length=max_length, padding=True, return_tensors="pt")
        enc.pop("token_type_ids", None)
        with torch.no_grad():
            probs.append(torch.softmax(model(**enc).logits, dim=-1).numpy())
    return np.concatenate(probs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--data-dir", default="research/data/splits")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-length", type=int, default=512)
    args = ap.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_dir).eval()
    # Model output order is id order; labels are upper-cased to match the dataset
    labels = [model.config.id2label[i].upper() for i in range(model.config.num_labels)]

    for split in ("val", "test"):
        df = load_split(args.data_dir, split)
        probs = predict(model, tokenizer, df["text"].tolist(), args.max_length)
        # evaluate.py expects probability columns in sorted label order
        order = np.argsort(labels)
        write_predictions(os.path.join(args.out, f"predictions_{split}.csv"), df, [labels[i] for i in order], probs[:, order])

    save_json(os.path.join(args.out, "run_info.json"), {"model": f"deployed: {os.path.basename(os.path.abspath(args.model_dir))}", "labels": sorted(labels)})
    print(f"Wrote predictions to {args.out}")


if __name__ == "__main__":
    main()
