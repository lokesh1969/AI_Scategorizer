import os
import shutil
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Tuple, List, Dict, Any
from backend.app.core.config import settings
from backend.app.pipeline.preprocessing import preprocess_image_for_ocr

# Use the default Windows install location when tesseract is not on PATH
_WINDOWS_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if not shutil.which("tesseract") and os.path.exists(_WINDOWS_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT

# Scanned PDFs are rendered at 300 DPI; cap pages so one upload cannot run for minutes
MAX_OCR_PAGES = 20


def check_tesseract_languages() -> List[str]:
    try:
        return pytesseract.get_languages(config="")
    except Exception:
        return []


def run_ocr_on_file(file_path: str, file_info: Dict[str, Any], doc_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Runs Tesseract OCR (eng+hin when available) on scanned images or scanned PDFs
    after image preprocessing. On failure returns empty text and records the
    error in metadata, so the error message is never classified as content.
    """
    ext = file_info["extension"]
    applied_preprocessing: List[str] = []
    preprocessed_img_path = ""
    error = None

    available_langs = check_tesseract_languages()
    ocr_lang = "eng+hin" if "hin" in available_langs else "eng"

    image_paths: List[str] = []
    page_texts: List[str] = []
    try:
        if ext in ["png", "jpg", "jpeg"]:
            image_paths.append(file_path)
        elif ext == "pdf":
            with fitz.open(file_path) as pdf_doc:
                for i, page in enumerate(pdf_doc):
                    if i >= MAX_OCR_PAGES:
                        break
                    img_path = os.path.join(settings.PDF_PAGES_DIR, f"{doc_id}_page_{i + 1}.png")
                    page.get_pixmap(dpi=300).save(img_path)
                    image_paths.append(img_path)

        for i, img_path in enumerate(image_paths):
            processed_path, steps, _ = preprocess_image_for_ocr(img_path, f"{doc_id}_p{i + 1}")
            if not preprocessed_img_path:
                preprocessed_img_path = processed_path
            applied_preprocessing.extend(steps)

            with Image.open(processed_path) as img:
                text = pytesseract.image_to_string(img, lang=ocr_lang, config="--psm 6")
            if text.strip():
                page_texts.append(text.strip())
    except Exception as e:
        print(f"[OCR Error] Error running Tesseract OCR on {file_path}: {e}")
        error = str(e)

    metadata = {
        "ocr_used": True,
        "language": ocr_lang,
        "preprocessing_applied": list(dict.fromkeys(applied_preprocessing)),
        "pages_processed": len(image_paths),
        "error": error,
        "preprocessed_image_url": (
            f"/api/documents/preprocessed-image/{os.path.basename(preprocessed_img_path)}"
            if preprocessed_img_path.startswith(settings.PREPROCESSED_DIR) else None
        ),
    }
    return "\n\n".join(page_texts).strip(), metadata
