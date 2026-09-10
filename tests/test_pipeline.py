import os
import pytest
from backend.app.pipeline.ingestion import validate_and_ingest_file
from backend.app.pipeline.language import detect_language
from backend.app.pipeline.cleaner import clean_and_normalize_text
from backend.app.pipeline.classifier import classifier_engine
from backend.app.pipeline.priority import calculate_priority
from backend.app.pipeline.summarizer import generate_summary
from backend.app.pipeline.ner import extract_entities
from backend.app.pipeline.sentiment import analyze_sentiment
from backend.app.pipeline.routing import route_document

def test_file_validation():
    valid, err, info = validate_and_ingest_file("sample.pdf", b"PDF content sample test string")
    assert valid is True
    assert info["extension"] == "pdf"

    invalid, err, info = validate_and_ingest_file("malicious.exe", b"executable content")
    assert invalid is False
    assert "Unsupported file type" in err

def test_bilingual_language_detection():
    assert detect_language("Emergency fire alarm triggered on platform 2.") == "English"
    assert detect_language("प्लेटफॉर्म नंबर 2 पर आपातकालीन स्थिति उत्पन्न हुई।") == "Hindi"
    assert detect_language("Platform 3 पर maintenance work urgently required.") == "Mixed (Hindi + English)"

def test_text_cleaner():
    raw = "  Emergency   fire   \n\n\n alarm detected.  "
    cleaned = clean_and_normalize_text(raw)
    assert "Emergency fire" in cleaned
    assert "\n\n\n" not in cleaned

def test_ai_classification_probability():
    classifier_engine.load_model()
    cat, conf, probs = classifier_engine.predict("Emergency fire alarm detected on platform 2 station area. Evacuate passengers immediately.")
    assert cat == "SAFETY"
    assert conf >= 40.0
    assert "SAFETY" in probs
    assert "FINANCE" in probs

def test_priority_engine():
    level, score, reason = calculate_priority("SAFETY", "Fire explosion emergency detected near platform.")
    assert level == "CRITICAL"
    assert score >= 85
    assert "fire" in reason or "emergency" in reason

def test_summarizer():
    text = "Emergency fire alarm detected on platform 2. Smoke rising near power transformer. Fire squad immediately notified. Station evacuation initiated for passenger safety."
    summary = generate_summary(text, max_sentences=2)
    assert len(summary) > 0
    assert "•" in summary

def test_ner_entity_extraction():
    text = "Invoice INV-4029 issued on 10 September 2026 for total amount ₹4,50,000 at Central Metro Station."
    entities = extract_entities(text)
    labels = [e["label"] for e in entities]
    assert "MONEY" in labels
    assert "DATE" in labels

def test_sentiment_analysis():
    res = analyze_sentiment("Emergency fire accident passenger injured severe distress.")
    assert res["label"] == "NEGATIVE"

def test_routing_confidence_threshold():
    dept, status = route_document("SAFETY", 95.0, 70.0)
    assert dept == "Station Controller"
    assert status == "AI VERIFIED"

    dept_low, status_low = route_document("SAFETY", 61.4, 70.0)
    assert dept_low == "Human Verification Queue"
    assert status_low == "HUMAN VERIFICATION REQUIRED"
