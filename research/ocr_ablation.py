"""
OCR preprocessing ablation: measures how much each image preprocessing step
changes Tesseract accuracy (character/word error rate).

Input folder: scanned images (png/jpg) each with a ground-truth transcript of the
same name, e.g. scan01.png + scan01.txt (UTF-8).

    python research/ocr_ablation.py --images research/data/ocr_eval --out research/results/ocr_ablation

Configurations: no preprocessing, full pipeline, and full pipeline minus one step.
"""
import argparse
import glob
import os
import sys
import tempfile

import pandas as pd
import pytesseract
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="ocr_ablation_"))
from backend.app.pipeline.ocr import check_tesseract_languages  # noqa: E402  (also sets tesseract path)
from backend.app.pipeline.preprocessing import ALL_STEPS, preprocess_image_for_ocr  # noqa: E402


def levenshtein(a, b) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def error_rates(ref: str, hyp: str):
    ref_c, hyp_c = " ".join(ref.split()), " ".join(hyp.split())
    ref_w, hyp_w = ref_c.split(), hyp_c.split()
    cer = levenshtein(ref_c, hyp_c) / max(1, len(ref_c))
    wer = levenshtein(ref_w, hyp_w) / max(1, len(ref_w))
    return cer, wer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--out", default="research/results/ocr_ablation")
    args = ap.parse_args()

    lang = "eng+hin" if "hin" in check_tesseract_languages() else "eng"
    configs = {"no_preprocessing": [], "full_pipeline": list(ALL_STEPS)}
    configs.update({f"without_{s}": [x for x in ALL_STEPS if x != s] for s in ALL_STEPS})

    images = [p for p in glob.glob(os.path.join(args.images, "*")) if p.lower().endswith((".png", ".jpg", ".jpeg"))]
    rows = []
    for img_path in images:
        gt_path = os.path.splitext(img_path)[0] + ".txt"
        if not os.path.exists(gt_path):
            print(f"skip {img_path}: no ground truth .txt")
            continue
        with open(gt_path, encoding="utf-8") as f:
            ref = f.read()
        stem = os.path.splitext(os.path.basename(img_path))[0]
        for name, steps in configs.items():
            processed, _, _ = preprocess_image_for_ocr(img_path, f"ablation_{stem}_{name}", steps=steps)
            with Image.open(processed) as im:
                hyp = pytesseract.image_to_string(im, lang=lang, config="--psm 6")
            cer, wer = error_rates(ref, hyp)
            rows.append({"image": stem, "config": name, "cer": cer, "wer": wer})
            print(f"{stem:<20} {name:<22} CER={cer:.3f} WER={wer:.3f}")

    if not rows:
        raise SystemExit("No image + .txt pairs found")
    os.makedirs(args.out, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(args.out, "per_image.csv"), index=False)
    summary = df.groupby("config")[["cer", "wer"]].mean().sort_values("cer")
    summary.to_csv(os.path.join(args.out, "summary.csv"))
    print("\nMean error rates (lower is better):\n", summary.round(4).to_string())


if __name__ == "__main__":
    main()
