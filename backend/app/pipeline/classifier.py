import os
import joblib
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from backend.app.core.config import settings

CATEGORIES = ["SAFETY", "FINANCE", "MAINTENANCE", "OPERATIONS"]

class DocumentClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        if os.path.exists(settings.MODEL_PATH):
            try:
                pipeline_data = joblib.load(settings.MODEL_PATH)
                self.vectorizer = pipeline_data["vectorizer"]
                self.model = pipeline_data["model"]
                self.is_loaded = True
                return
            except Exception as e:
                print(f"[Classifier Error] Error loading {settings.MODEL_PATH}: {e}")

        # Fallback baseline model
        training_corpus = [
            ("Emergency fire alarm incident detected on platform 2 station area. Evacuate passengers immediately.", "SAFETY"),
            ("Accidents report passenger injury near escalator. Medical assistance requested immediately.", "SAFETY"),
            ("Hazard report gas leak near electrical room. Safety instructions issued to staff.", "SAFETY"),
            ("प्लेटफॉर्म नंबर 2 पर आपातकालीन स्थिति उत्पन्न हुई। अग्निशामक टीम को सूचित किया गया।", "SAFETY"),
            ("Invoice #4029 purchase order payment clearance for electrical equipment total amount ₹4,50,000.", "FINANCE"),
            ("Quarterly expenditure report budget allocation statement for Q3 railway infrastructure.", "FINANCE"),
            ("Track fault machinery failure maintenance schedule required urgently for train 102.", "MAINTENANCE"),
            ("Equipment repair request HVAC system breakdown at Metro Station Central.", "MAINTENANCE"),
            ("Daily station operational report train arrival schedule platform management administrative log.", "OPERATIONS"),
            ("Shift handover log operational delay Metro line schedule optimization report.", "OPERATIONS")
        ]

        texts = [t[0] for t in training_corpus]
        labels = [t[1] for t in training_corpus]

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        X = self.vectorizer.fit_transform(texts)

        self.model = LogisticRegression(C=10.0, max_iter=200, random_state=42)
        self.model.fit(X, labels)
        self.is_loaded = True

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        if not text or not text.strip():
            return "OPERATIONS", 50.0, {cat: 25.0 for cat in CATEGORIES}

        if not self.is_loaded:
            self.load_model()

        X_vec = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X_vec)[0]
        classes = self.model.classes_

        prob_dict = {cat: 0.0 for cat in CATEGORIES}
        for cls, prob in zip(classes, probs):
            prob_dict[cls] = round(float(prob * 100.0), 1)

        best_category = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[best_category]

        return best_category, confidence, prob_dict

classifier_engine = DocumentClassifier()
