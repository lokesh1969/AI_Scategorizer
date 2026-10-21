"""
Evaluates one or more runs (directories containing predictions_val.csv and
predictions_test.csv) and writes paper-ready metrics, tables and figures.

    python research/evaluate.py research/results/tfidf_lr research/results/distilbert research/results/muril
    python research/evaluate.py research/results/* --target-accuracy 0.95 --out research/results/report

Methodology (important for a fair paper):
  * Temperature scaling and the routing threshold are fitted on VALIDATION only,
    then reported on TEST, so the test set never influences any choice.
  * 95% confidence intervals come from 1000 bootstrap resamples of the test set.
  * Paired McNemar tests compare runs evaluated on the same test documents.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from common import read_predictions, save_json

EPS = 1e-12


# ---------------------------------------------------------------- calibration
def apply_temperature(probs: np.ndarray, T: float) -> np.ndarray:
    logits = np.log(np.clip(probs, EPS, 1.0)) / T
    logits -= logits.max(axis=1, keepdims=True)
    e = np.exp(logits)
    return e / e.sum(axis=1, keepdims=True)


def nll(probs: np.ndarray, y: np.ndarray) -> float:
    return float(-np.mean(np.log(np.clip(probs[np.arange(len(y)), y], EPS, 1.0))))


def fit_temperature(probs: np.ndarray, y: np.ndarray) -> float:
    res = minimize_scalar(lambda T: nll(apply_temperature(probs, T), y), bounds=(0.05, 10.0), method="bounded")
    return float(res.x)


def ece(probs: np.ndarray, y: np.ndarray, n_bins: int = 15):
    """Expected Calibration Error plus per-bin data for a reliability diagram."""
    conf = probs.max(axis=1)
    correct = probs.argmax(axis=1) == y
    edges = np.linspace(0, 1, n_bins + 1)
    total, bins = 0.0, []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf > lo) & (conf <= hi)
        if mask.any():
            acc, avg_conf = correct[mask].mean(), conf[mask].mean()
            total += mask.mean() * abs(acc - avg_conf)
            bins.append({"lo": lo, "hi": hi, "count": int(mask.sum()), "accuracy": float(acc), "confidence": float(avg_conf)})
    return float(total), bins


def brier(probs: np.ndarray, y: np.ndarray) -> float:
    onehot = np.eye(probs.shape[1])[y]
    return float(np.mean(np.sum((probs - onehot) ** 2, axis=1)))


# ---------------------------------------------------------- selective routing
def threshold_sweep(conf: np.ndarray, correct: np.ndarray, thresholds):
    """
    For each threshold t, documents with confidence >= t are auto-routed and the
    rest go to human review (assumed correct after review).
    """
    rows = []
    n = len(conf)
    for t in thresholds:
        auto = conf >= t
        coverage = auto.mean()
        sel_acc = correct[auto].mean() if auto.any() else float("nan")
        rows.append({
            "threshold": round(float(t), 3),
            "auto_routed_pct": round(100 * coverage, 2),
            "human_review_pct": round(100 * (1 - coverage), 2),
            "auto_routed_accuracy": round(float(sel_acc), 4) if auto.any() else None,
            "misrouted_docs_per_1000": round(1000 * float((auto & ~correct).sum()) / n, 1),
            "system_accuracy_with_review": round(float((correct & auto).sum() + (~auto).sum()) / n, 4),
        })
    return rows


def aurc(conf: np.ndarray, correct: np.ndarray) -> float:
    """Area under the risk-coverage curve (lower is better)."""
    order = np.argsort(-conf)
    errors = (~correct[order]).astype(float)
    risks = np.cumsum(errors) / np.arange(1, len(errors) + 1)
    return float(risks.mean())


def pick_threshold(conf: np.ndarray, correct: np.ndarray, target: float) -> float:
    """Lowest threshold whose auto-routed accuracy on VALIDATION reaches the target."""
    for t in np.round(np.arange(0.0, 1.0, 0.01), 2):
        auto = conf >= t
        if auto.sum() >= 5 and correct[auto].mean() >= target:
            return float(t)
    return 1.0


# -------------------------------------------------------------- statistics
def bootstrap_ci(y, pred, fn, n=1000, seed=0):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y))
    scores = [fn(y[s], pred[s]) for s in (rng.choice(idx, len(idx)) for _ in range(n))]
    return [round(float(np.percentile(scores, 2.5)), 4), round(float(np.percentile(scores, 97.5)), 4)]


def mcnemar(correct_a: np.ndarray, correct_b: np.ndarray):
    b = int((correct_a & ~correct_b).sum())
    c = int((~correct_a & correct_b).sum())
    p = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    return {"a_right_b_wrong": b, "a_wrong_b_right": c, "p_value": float(p)}


# ------------------------------------------------------------------ plotting
def plot_all(out_dir, name, labels, cm, bins_before, bins_after, sweep):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping figures")
        return

    fig, ax = plt.subplots(figsize=(5, 4.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels, rotation=30)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im)
    ax.set_title(f"Confusion matrix: {name}")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "confusion_matrix.png"), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")
    for bins, lab in ((bins_before, "Uncalibrated"), (bins_after, "Temperature scaled")):
        ax.plot([b["confidence"] for b in bins], [b["accuracy"] for b in bins], "o-", label=lab)
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Reliability: {name}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "reliability.png"), dpi=200)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(6, 4))
    t = [r["threshold"] for r in sweep]
    ax1.plot(t, [r["auto_routed_pct"] for r in sweep], label="Auto-routed %")
    ax1.set_xlabel("Confidence threshold")
    ax1.set_ylabel("Auto-routed (%)")
    ax2 = ax1.twinx()
    ax2.plot(t, [100 * r["auto_routed_accuracy"] if r["auto_routed_accuracy"] is not None else np.nan for r in sweep],
             color="tab:orange", label="Accuracy of auto-routed %")
    ax2.set_ylabel("Accuracy of auto-routed docs (%)")
    fig.legend(loc="lower left", bbox_to_anchor=(0.12, 0.15))
    ax1.set_title(f"Threshold trade-off: {name}")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "threshold_tradeoff.png"), dpi=200)
    plt.close(fig)


# ------------------------------------------------------------------- main
def evaluate_run(run_dir: str, target: float):
    name = os.path.basename(os.path.normpath(run_dir))
    val_df, labels, val_probs = read_predictions(os.path.join(run_dir, "predictions_val.csv"))
    test_df, labels_t, test_probs = read_predictions(os.path.join(run_dir, "predictions_test.csv"))
    assert labels == labels_t, "val/test label columns differ"
    lab2i = {l: i for i, l in enumerate(labels)}
    y_val, y_test = val_df["label"].map(lab2i), test_df["label"].map(lab2i)
    if y_val.isnull().any() or y_test.isnull().any():
        raise ValueError(f"{name}: some gold labels are not in the model label set {labels}")
    y_val, y_test = y_val.astype(int).to_numpy(), y_test.astype(int).to_numpy()
    pred = test_probs.argmax(axis=1)

    T = fit_temperature(val_probs, y_val)
    test_cal = apply_temperature(test_probs, T)
    val_cal = apply_temperature(val_probs, T)

    ece_raw, bins_raw = ece(test_probs, y_test)
    ece_cal, bins_cal = ece(test_cal, y_test)

    correct = pred == y_test
    threshold = pick_threshold(val_cal.max(axis=1), val_cal.argmax(axis=1) == y_val, target)
    sweep = threshold_sweep(test_cal.max(axis=1), correct, np.round(np.arange(0.0, 1.0, 0.05), 2))
    chosen = threshold_sweep(test_cal.max(axis=1), correct, [threshold])[0]

    per_language = {}
    for lang, g in test_df.groupby("language"):
        idx = g.index.to_numpy()
        per_language[str(lang)] = {
            "n": int(len(idx)),
            "accuracy": round(float(accuracy_score(y_test[idx], pred[idx])), 4),
            "macro_f1": round(float(f1_score(y_test[idx], pred[idx], average="macro", labels=sorted(set(y_test[idx])), zero_division=0)), 4),
        }

    # Macro-F1 averages only over classes present in the test set (a cross-source test
    # set may lack a class); predictions of absent classes still count as errors.
    present = sorted(set(y_test))
    macro = lambda a, b: f1_score(a, b, average="macro", labels=present, zero_division=0)
    cm = confusion_matrix(y_test, pred, labels=range(len(labels)))
    run_info = {}
    info_path = os.path.join(run_dir, "run_info.json")
    if os.path.exists(info_path):
        with open(info_path, encoding="utf-8") as f:
            run_info = json.load(f)

    metrics = {
        "run": name,
        "model": run_info.get("model", name),
        "n_test": int(len(y_test)),
        "classes_in_test": [labels[i] for i in present],
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "accuracy_95ci": bootstrap_ci(y_test, pred, accuracy_score),
        "macro_f1": round(float(macro(y_test, pred)), 4),
        "macro_f1_95ci": bootstrap_ci(y_test, pred, macro),
        "weighted_f1": round(float(f1_score(y_test, pred, average="weighted")), 4),
        "per_class": classification_report(y_test, pred, labels=range(len(labels)), target_names=labels, output_dict=True, zero_division=0),
        "per_language": per_language,
        "confusion_matrix": {"labels": labels, "matrix": cm.tolist()},
        "calibration": {
            "temperature": round(T, 4),
            "ece_before": round(ece_raw, 4),
            "ece_after": round(ece_cal, 4),
            "nll_before": round(nll(test_probs, y_test), 4),
            "nll_after": round(nll(test_cal, y_test), 4),
            "brier_before": round(brier(test_probs, y_test), 4),
            "brier_after": round(brier(test_cal, y_test), 4),
        },
        "selective_routing": {
            "target_auto_accuracy": target,
            "threshold_chosen_on_val": threshold,
            "test_at_threshold": chosen,
            "aurc": round(aurc(test_cal.max(axis=1), correct), 4),
            "sweep": sweep,
        },
        "run_info": run_info,
    }

    out_dir = os.path.join(run_dir, "eval")
    os.makedirs(out_dir, exist_ok=True)
    save_json(os.path.join(out_dir, "metrics.json"), metrics)
    pd.DataFrame(sweep).to_csv(os.path.join(out_dir, "threshold_sweep.csv"), index=False)
    errors = test_df.loc[~correct, ["id", "language", "label", "pred", "confidence", "text"]]
    errors.assign(text=errors["text"].str.slice(0, 300)).to_csv(os.path.join(out_dir, "errors.csv"), index=False, encoding="utf-8")
    plot_all(out_dir, name, labels, cm, bins_raw, bins_cal, sweep)
    return metrics, test_df["id"].to_numpy(), correct


def fmt_ci(v, ci):
    return f"{100 * v:.1f} [{100 * ci[0]:.1f}, {100 * ci[1]:.1f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="run directories containing predictions_*.csv")
    ap.add_argument("--target-accuracy", type=float, default=0.95,
                    help="required accuracy of auto-routed documents when picking the threshold")
    ap.add_argument("--out", default="research/results/report")
    args = ap.parse_args()

    runs = [r for r in args.runs if os.path.exists(os.path.join(r, "predictions_test.csv"))]
    missing = sorted(set(args.runs) - set(runs))
    if missing:
        print("WARNING: no predictions_test.csv (training failed or not run) for: " + ", ".join(missing))
    if not runs:
        raise SystemExit("No runs to evaluate.")
    results = [evaluate_run(r, args.target_accuracy) for r in runs]

    lines = ["# Experiment results", "",
             f"Threshold target: auto-routed accuracy >= {args.target_accuracy:.0%} (chosen on validation, reported on test).", "",
             "## Main results (test set, 95% bootstrap CI)", "",
             "| Run | Accuracy % | Macro-F1 % | ECE before → after | Threshold | Auto-routed % | Auto-routed acc. % | AURC |",
             "|---|---|---|---|---|---|---|---|"]
    for m, _, _ in results:
        s, c = m["selective_routing"], m["calibration"]
        acc = s["test_at_threshold"]["auto_routed_accuracy"]
        lines.append(
            f"| {m['run']} | {fmt_ci(m['accuracy'], m['accuracy_95ci'])} | {fmt_ci(m['macro_f1'], m['macro_f1_95ci'])} "
            f"| {c['ece_before']:.3f} → {c['ece_after']:.3f} | {s['threshold_chosen_on_val']:.2f} "
            f"| {s['test_at_threshold']['auto_routed_pct']:.1f} | {'-' if acc is None else f'{100 * acc:.1f}'} | {s['aurc']:.4f} |")

    languages = sorted({lang for m, _, _ in results for lang in m["per_language"]})
    if len(languages) > 1:
        lines += ["", "## Macro-F1 by language (test)", "", "| Run | " + " | ".join(languages) + " |",
                  "|---|" + "---|" * len(languages)]
        for m, _, _ in results:
            cells = [f"{100 * m['per_language'][l]['macro_f1']:.1f} (n={m['per_language'][l]['n']})" if l in m["per_language"] else "-" for l in languages]
            lines.append(f"| {m['run']} | " + " | ".join(cells) + " |")

    if len(results) > 1:
        lines += ["", "## Paired McNemar tests (test)", "", "| A | B | A right, B wrong | A wrong, B right | p-value |", "|---|---|---|---|---|"]
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                (ma, ids_a, ca), (mb, ids_b, cb) = results[i], results[j]
                if not np.array_equal(ids_a, ids_b):
                    lines.append(f"| {ma['run']} | {mb['run']} | - | - | different test sets |")
                    continue
                t = mcnemar(ca, cb)
                lines.append(f"| {ma['run']} | {mb['run']} | {t['a_right_b_wrong']} | {t['a_wrong_b_right']} | {t['p_value']:.4g} |")

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nPer-run details, figures and error lists are in <run>/eval/. Summary: {args.out}/results.md")


if __name__ == "__main__":
    main()
