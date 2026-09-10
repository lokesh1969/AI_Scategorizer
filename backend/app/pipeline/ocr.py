import os
import fitz # PyMuPDF
import pytesseract
from PIL import Image
from typing import Tuple, List, Dict, Any
from backend.app.pipeline.preprocessing import preprocess_image_for_ocr

# Verify pytesseract binary path if needed
def check_tesseract_languages() -> List[str]:
    try:
        langs = pytesseract.get_languages(config='')
        return langs
    except Exception:
        return []

def run_ocr_on_file(file_path: str, file_info: Dict[str, Any], doc_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Runs Tesseract OCR on scanned images or scanned PDFs after applying image preprocessing.
    Configures bilingual OCR language (eng+hin).
    """
    ext = file_info["extension"]
    ocr_text = ""
    applied_preprocessing = []
    preprocessed_img_path = ""
    
    available_langs = check_tesseract_languages()
    ocr_lang = "eng"
    if "hin" in available_langs:
        ocr_lang = "eng+hin"
    elif "eng" not in available_langs and available_langs:
        ocr_lang = available_langs[0]

    image_paths_to_process = []

    try:
        if ext in ["png", "jpg", "jpeg"]:
            image_paths_to_process.append(file_path)

        elif ext == "pdf":
            # Convert scanned PDF pages to images using PyMuPDF (fitz) or pdf2image
            pdf_doc = fitz.open(file_path)
            temp_img_dir = os.path.join(os.path.dirname(file_path), "pdf_pages")
            os.makedirs(temp_img_dir, exist_ok=True)

            for i, page in enumerate(pdf_doc):
                pix = page.get_pixmap(dpi=300)
                img_path = os.path.join(temp_img_dir, f"{doc_id}_page_{i+1}.png")
                pix.save(img_path)
                image_paths_to_process.append(img_path)

        page_texts = []
        for i, img_path in enumerate(image_paths_to_process):
            # Preprocess image
            processed_path, steps, _ = preprocess_image_for_ocr(img_path, f"{doc_id}_p{i+1}")
            if not preprocessed_img_path:
                preprocessed_img_path = processed_path
            applied_preprocessing.extend(steps)

            # Open image for pytesseract
            img = Image.open(processed_path)
            
            # Execute Tesseract OCR
            text = pytesseract.image_to_string(img, lang=ocr_lang, config='--psm 6')
            if text.strip():
                page_texts.append(text.strip())

        ocr_text = "\n\n".join(page_texts)

    except Exception as e:
        print(f"[OCR Error] Error running Tesseract OCR on {file_path}: {e}")
        ocr_text = f"OCR Error: {e}"

    # Unique preprocessing steps list
    applied_preprocessing = list(dict.fromkeys(applied_preprocessing))

    metadata = {
        "ocr_used": True,
        "language": ocr_lang,
        "preprocessing_applied": applied_preprocessing,
        "preprocessed_image_url": f"/api/documents/preprocessed-image/{os.path.basename(preprocessed_img_path)}" if preprocessed_img_path else None
    }

    return ocr_text.strip(), metadata
