import os
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any
from backend.app.core.config import settings

def preprocess_image_for_ocr(input_image_path: str, output_filename_prefix: str) -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Applies image preprocessing pipeline to optimize document quality for Tesseract OCR.
    Pipeline steps:
    1. Grayscale Conversion
    2. Resizing/Upscaling (DPI optimization)
    3. CLAHE Contrast Enhancement
    4. Median Denoising
    5. Adaptive Thresholding (Otsu binarization)
    6. Sharpening filter
    7. Deskewing / Rotation correction
    Returns: (preprocessed_image_path, applied_steps_list, metadata)
    """
    applied_steps = []
    metadata = {}

    try:
        # Load image with OpenCV
        image = cv2.imread(input_image_path)
        if image is None:
            # Fallback PIL load
            pil_img = Image.open(input_image_path).convert('RGB')
            image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        h, w = image.shape[:2]
        metadata["original_dimensions"] = f"{w}x{h}"

        # 1. Grayscale Conversion
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        applied_steps.append("Grayscale Conversion")

        # 2. Resizing/Upscaling if low resolution
        if min(w, h) < 1000:
            scale_factor = 2.0
            gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            applied_steps.append("DPI Upscaling (2.0x)")

        # 3. CLAHE Contrast Enhancement (Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        applied_steps.append("CLAHE Contrast Enhancement")

        # 4. Noise Removal / Denoising
        denoised = cv2.medianBlur(enhanced, 3)
        applied_steps.append("Median Denoising")

        # 5. Adaptive Thresholding / Binarization (Otsu's Thresholding)
        _, binarized = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        applied_steps.append("Adaptive Binarization (Otsu)")

        # 6. Sharpening Filter
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(binarized, -1, sharpen_kernel)
        applied_steps.append("Sharpening")

        # 7. Deskewing / Rotation Correction
        coords = np.column_stack(np.where(sharpened > 0))
        angle = 0.0
        if len(coords) > 0:
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
        
        if abs(angle) > 0.5 and abs(angle) < 45.0:
            (h_proc, w_proc) = sharpened.shape[:2]
            center = (w_proc // 2, h_proc // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            final_processed = cv2.warpAffine(sharpened, M, (w_proc, h_proc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            applied_steps.append(f"Deskewing ({angle:.1f}°)")
        else:
            final_processed = sharpened

        # Save preprocessed image
        os.makedirs(settings.PREPROCESSED_DIR, exist_ok=True)
        save_filename = f"preprocessed_{output_filename_prefix}.png"
        save_path = os.path.join(settings.PREPROCESSED_DIR, save_filename)
        cv2.imwrite(save_path, final_processed)

        metadata["preprocessed_dimensions"] = f"{final_processed.shape[1]}x{final_processed.shape[0]}"
        return save_path, applied_steps, metadata

    except Exception as e:
        print(f"[Preprocessing Error] Error preprocessing image {input_image_path}: {e}")
        # Return input image path as fallback
        return input_image_path, ["Fallback (Original Image Used)"], {"error": str(e)}
