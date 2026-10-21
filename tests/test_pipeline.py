import numpy as np
import cv2
from backend.app.pipeline.ingestion import validate_and_ingest_file
from backend.app.pipeline.language import detect_language
from backend.app.pipeline.cleaner import clean_and_normalize_text
from backend.app.pipeline.classifier import classifier_engine, UNCLASSIFIED
from backend.app.pipeline.priority import calculate_priority
from backend.app.pipeline.summarizer import generate_summary
from backend.app.pipeline.ner import extract_entities
from backend.app.pipeline.sentiment import analyze_sentiment
from backend.app.pipeline.routing import route_document
from backend.app.pipeline.preprocessing import estimate_skew_angle, rotate_image
from backend.app.pipeline.text_utils import find_keywords


def test_file_validation():
    valid, err, info = validate_and_ingest_file("sample.pdf", b"PDF content sample test string")
    assert valid is True
    assert info["extension"] == "pdf"

    invalid, err, info = validate_and_ingest_file("malicious.exe", b"executable content")
    assert invalid is False
    assert "Unsupported file type" in err


def test_bilingual_language_detection():
    assert detect_language("Please review the attached vendor contract before signing.") == "English"
    assert detect_language("कृपया संलग्न अनुबंध की समीक्षा करें और हस्ताक्षर से पहले टिप्पणी दें।") == "Hindi"
    assert detect_language("Platform 3 पर maintenance work urgently required.") == "Mixed (Hindi + English)"
    # One English acronym inside a long Hindi sentence is still Hindi
    assert detect_language("कृपया इस महीने का वेतन विवरण और छुट्टी का रिकॉर्ड संलग्न PDF में भेजें धन्यवाद") == "Hindi"


def test_text_cleaner():
    cleaned = clean_and_normalize_text("  Quarterly   budget   \n\n\n report attached.  ")
    assert "Quarterly budget" in cleaned
    assert "\n\n\n" not in cleaned


def test_keyword_matching_uses_whole_tokens():
    assert find_keywords("Fire in the server room", ["fire"]) == ["fire"]
    assert find_keywords("Firewall configuration update", ["fire"]) == []
    assert find_keywords("The employee was fired", ["fire"]) == []
    assert find_keywords("ट्रेन आगमन समय सारणी", ["आग"]) == []  # arrival, not fire
    assert find_keywords("गोदाम में आग लगी", ["आग"]) == ["आग"]
    assert find_keywords("A legal notice was served", ["legal notice"]) == ["legal notice"]


def test_empty_text_is_never_auto_routed():
    cat, conf, _ = classifier_engine.predict("")
    assert cat == UNCLASSIFIED and conf == 0.0
    dept, status = route_document(cat, conf, 0.0)  # even with a zero threshold
    assert status == "HUMAN VERIFICATION REQUIRED"


def test_priority_engine():
    level, score, reason = calculate_priority("OPERATIONS", "Fire and explosion emergency reported in warehouse 4.")
    assert level == "CRITICAL" and score >= 85
    assert "fire" in reason

    level, _, _ = calculate_priority("OPERATIONS", "Firewall configuration update for the office.")
    assert level != "CRITICAL"

    level, _, _ = calculate_priority("LEGAL", "We received a legal notice; the lawsuit hearing deadline is Friday.")
    assert level in ("HIGH", "CRITICAL")


def test_summarizer():
    text = ("The quarterly budget review is scheduled for Monday. Finance will present the variance report. "
            "All department heads must submit expense forecasts. Late submissions will delay approval.")
    summary = generate_summary(text, max_sentences=2)
    assert summary.count("•") == 2


def test_ner_entity_extraction():
    text = "Invoice INV-4029 issued on 10 September 2026 for total amount ₹4,50,000 to Acme Supplies Pvt Ltd."
    entities = extract_entities(text)
    by_label = {e["label"]: e["text"] for e in entities}
    assert "MONEY" in by_label and "DATE" in by_label
    assert by_label["DOCUMENT_NUMBER"] == "INV-4029"
    assert "ORGANIZATION" in by_label


def test_ner_ignores_word_fragments():
    entities = extract_entities("Please see the Documentation and Billing Reporting for the Identity team.")
    assert [e for e in entities if e["label"] == "DOCUMENT_NUMBER"] == []


def test_sentiment_analysis():
    assert analyze_sentiment("Payment rejected; penalty applied for overdue invoice and a complaint filed.")["label"] == "NEGATIVE"
    assert analyze_sentiment("Goods received per invoice.")["label"] == "NEUTRAL"


def test_routing_confidence_threshold():
    dept, status = route_document("LEGAL", 95.0, 70.0)
    assert dept == "Legal Counsel" and status == "AI VERIFIED"

    dept_low, status_low = route_document("LEGAL", 61.4, 70.0)
    assert dept_low == "Human Verification Queue"
    assert status_low == "HUMAN VERIFICATION REQUIRED"


def _synthetic_page(angle: float) -> np.ndarray:
    page = np.full((800, 1000), 255, np.uint8)
    for y in range(150, 650, 40):
        cv2.line(page, (150, y), (850, y), 0, 6)
    return rotate_image(page, angle)


def test_deskew_estimates_and_corrects_rotation():
    for angle in (-7.0, -3.0, 4.0, 8.0):
        rotated = _synthetic_page(angle)
        estimated = estimate_skew_angle(rotated)
        assert abs(estimated - angle) < 1.0, (angle, estimated)
        corrected = rotate_image(rotated, -estimated)
        assert abs(estimate_skew_angle(corrected)) < 1.0
