"""
Fine-tunes a Hugging Face encoder for department classification on the fixed split.
Run it once per model to compare English-only vs multilingual encoders:

    python research/train_transformer.py --model-name distilbert-base-uncased        --out research/results/distilbert
    python research/train_transformer.py --model-name distilbert-base-multilingual-cased --out research/results/mdistilbert
    python research/train_transformer.py --model-name google/muril-base-cased        --out research/results/muril
    python research/train_transformer.py --model-name xlm-roberta-base               --out research/results/xlmr

The best epoch is chosen on validation macro-F1. The saved model in <out>/model
can be served by the app: copy it to models/classifier (or set MODEL_DIR).
A GPU (e.g. free Google Colab T4) is strongly recommended.
"""
import argparse
import dataclasses
import os
import time

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

from common import label_list, load_split, save_json, set_seed, write_predictions


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, df, tokenizer, label2id, max_length):
        self.enc = tokenizer(df["text"].tolist(), truncation=True, max_length=max_length)
        self.labels = [label2id[l] for l in df["label"]]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        item = {k: v[i] for k, v in self.enc.items()}
        item["labels"] = self.labels[i]
        return item


def compute_metrics(eval_pred):
    logits, y = eval_pred
    pred = logits.argmax(axis=-1)
    return {"accuracy": accuracy_score(y, pred), "macro_f1": f1_score(y, pred, average="macro")}


def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--data-dir", default="research/data/splits")
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    set_seed(args.seed)

    train, val, test = (load_split(args.data_dir, s) for s in ("train", "val", "test"))
    labels = label_list(train)
    label2id = {l: i for i, l in enumerate(labels)}

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name, num_labels=len(labels), id2label=dict(enumerate(labels)), label2id=label2id
    )
    ds = {name: TextDataset(df, tokenizer, label2id, args.max_length) for name, df in (("train", train), ("val", val), ("test", test))}

    # Argument names changed across transformers versions: 5.x removed `warmup_ratio`
    # (a float `warmup_steps` < 1 is now a ratio) and older 4.x used `evaluation_strategy`.
    arg_fields = {f.name for f in dataclasses.fields(TrainingArguments)}
    version_kwargs = {"warmup_ratio": 0.1} if "warmup_ratio" in arg_fields else {"warmup_steps": 0.1}
    version_kwargs["eval_strategy" if "eval_strategy" in arg_fields else "evaluation_strategy"] = "epoch"

    training_args = TrainingArguments(
        output_dir=os.path.join(args.out, "checkpoints"),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        weight_decay=0.01,
        **version_kwargs,
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        fp16=torch.cuda.is_available(),
        seed=args.seed,
        report_to="none",
        logging_steps=50,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["val"],
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    start = time.perf_counter()
    trainer.train()
    train_minutes = (time.perf_counter() - start) / 60

    val_logits = trainer.predict(ds["val"]).predictions
    start = time.perf_counter()
    test_logits = trainer.predict(ds["test"]).predictions
    ms_per_doc = (time.perf_counter() - start) * 1000 / max(1, len(test))

    write_predictions(os.path.join(args.out, "predictions_val.csv"), val, labels, softmax(val_logits))
    write_predictions(os.path.join(args.out, "predictions_test.csv"), test, labels, softmax(test_logits))

    model_dir = os.path.join(args.out, "model")
    trainer.save_model(model_dir)
    tokenizer.save_pretrained(model_dir)

    save_json(os.path.join(args.out, "run_info.json"), {
        "model": args.model_name,
        "labels": labels,
        "seed": args.seed,
        "epochs": args.epochs,
        "learning_rate": args.lr,
        "batch_size": args.batch_size,
        "max_length": args.max_length,
        "best_checkpoint": trainer.state.best_model_checkpoint,
        "val_macro_f1": round(float(trainer.state.best_metric), 4),
        "train_minutes": round(train_minutes, 2),
        "inference_ms_per_doc": round(ms_per_doc, 3),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "parameters_millions": round(sum(p.numel() for p in model.parameters()) / 1e6, 1),
        "train_size": len(train),
    })
    print(f"Saved {args.model_name} to {model_dir}")


if __name__ == "__main__":
    main()
