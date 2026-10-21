import os
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any, Optional, Iterable
from backend.app.core.config import settings

ALL_STEPS = ("upscale", "clahe", "denoise", "sharpen", "deskew", "binarize")


def estimate_skew_angle(gray: np.ndarray) -> float:
    """
    Estimates document skew in degrees from the dark (text) pixels.
    Positive result = text lines rise to the right. Uses the minimum-area
    rectangle around text pixels, normalised to (-45, 45] so it works with
    both pre- and post-4.5 OpenCV angle conventions.
    """
    _, text_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ys, xs = np.nonzero(text_mask)
    if len(xs) < 50:
        return 0.0
    points = np.column_stack((xs, ys)).astype(np.float32)
    (_, _), (w, h), angle = cv2.minAreaRect(points)
    # Bring the angle of the rectangle's long side into (-45, 45]
    if w < h:
        angle -= 90
    while angle <= -45:
        angle += 90
    while angle > 45:
        angle -= 90
    # Image y axis points down, so a rectangle rotated by +a (clockwise on screen)
    # means text falls to the right; report rise-to-the-right as positive.
    return -float(angle)


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotates counter-clockwise by `angle` degrees (OpenCV convention) with white fill."""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=255)


def preprocess_image_for_ocr(
    input_image_path: str,
    output_filename_prefix: str,
    steps: Optional[Iterable[str]] = None,
) -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Image preprocessing for Tesseract OCR. Order:
      grayscale -> upscale (if small) -> CLAHE contrast -> median denoise
      -> unsharp sharpen -> deskew -> Otsu binarisation
    `steps` selects a subset of ALL_STEPS (used by research/ocr_ablation.py);
    None applies all of them.
    Returns: (preprocessed_image_path, applied_steps_list, metadata)
    """
    enabled = set(ALL_STEPS if steps is None else steps)
    applied: List[str] = []
    metadata: Dict[str, Any] = {}

    try:
        image = cv2.imread(input_image_path)
        if image is None:
            with Image.open(input_image_path) as pil_img:
                image = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)

        h, w = image.shape[:2]
        metadata["original_dimensions"] = f"{w}x{h}"

        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        applied.append("Grayscale Conversion")

        if "upscale" in enabled and min(w, h) < 1000:
            img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            applied.append("DPI Upscaling (2.0x)")

        if "clahe" in enabled:
            img = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img)
            applied.append("CLAHE Contrast Enhancement")

        if "denoise" in enabled:
            img = cv2.medianBlur(img, 3)
            applied.append("Median Denoising")

        if "sharpen" in enabled:
            blurred = cv2.GaussianBlur(img, (0, 0), 1.0)
            img = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
            applied.append("Unsharp Masking")

        if "deskew" in enabled:
            skew = estimate_skew_angle(img)
            metadata["skew_angle"] = round(skew, 2)
            if 0.5 < abs(skew) < 45:
                # Rotate clockwise by the rise angle to level the text lines
                img = rotate_image(img, -skew)
                applied.append(f"Deskewing ({skew:.1f}°)")

        if "binarize" in enabled:
            _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            applied.append("Otsu Binarization")

        save_path = os.path.join(settings.PREPROCESSED_DIR, f"preprocessed_{output_filename_prefix}.png")
        cv2.imwrite(save_path, img)
        metadata["preprocessed_dimensions"] = f"{img.shape[1]}x{img.shape[0]}"
        return save_path, applied, metadata

    except Exception as e:
        print(f"[Preprocessing Error] Error preprocessing image {input_image_path}: {e}")
        return input_image_path, ["Fallback (Original Image Used)"], {"error": str(e)}
