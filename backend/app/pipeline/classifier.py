import os
from typing import Dict, Tuple
from backend.app.core.config import settings
from backend.app.core.categories import CATEGORIES

# Category returned when there is nothing to classify (blank scan, failed OCR,
# missing model). It is not in DEPARTMENT_MAP, so routing always sends it to
# the human verification queue instead of auto-approving it.
UNCLASSIFIED = "UNCLASSIFIED"

# Minimum non-whitespace characters before the model output is trusted
MIN_TEXT_CHARS = 20


class DocumentClassifier:
    """Wraps a fine-tuned Hugging Face sequence classifier (see research/train_transformer.py)."""

    def __init__(self, model_dir: str = settings.MODEL_DIR):
        self.model_dir = model_dir
        self.hf_model = None
        self.hf_tokenizer = None
        self.is_loaded = False
        self.model_name = "none"
        self.load_model()

    def load_model(self):
        if not os.path.exists(os.path.join(self.model_dir, "config.json")):
            print(f"[Classifier] No model found at {self.model_dir}. Documents will go to human verification.")
            return
        try:
            # Imported lazily so the API (and its tests) can start without torch installed
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            self.hf_tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            self.hf_model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
            self.hf_model.eval()
            self.model_name = getattr(self.hf_model.config, "_name_or_path", None) or os.path.basename(self.model_dir)
            self.is_loaded = True
        except Exception as e:
            print(f"[Classifier Error] Error loading model from {self.model_dir}: {e}")

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Returns (category, confidence %, {category: probability %})."""
        empty_probs = {cat: 0.0 for cat in CATEGORIES}
        if not text or len("".join(text.split())) < MIN_TEXT_CHARS:
            return UNCLASSIFIED, 0.0, empty_probs

        if not self.is_loaded:
            self.load_model()
        if not self.is_loaded:
            return UNCLASSIFIED, 0.0, empty_probs

        import torch
        inputs = self.hf_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs.pop("token_type_ids", None)

        with torch.no_grad():
            logits = self.hf_model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        id2label = self.hf_model.config.id2label
        prob_dict = {id2label[i].upper(): round(float(p) * 100.0, 1) for i, p in enumerate(probs)}

        best_idx = int(torch.argmax(probs).item())
        best_category = id2label[best_idx].upper()
        confidence = round(float(probs[best_idx]) * 100.0, 1)
        return best_category, confidence, prob_dict


classifier_engine = DocumentClassifier()
