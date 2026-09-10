import os
from typing import Tuple, Dict, Any

ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'txt': 'text/plain',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # 25 MB

def validate_and_ingest_file(filename: str, file_bytes: bytes) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded document for file extension, size, and corruption.
    Returns: (is_valid, error_message, file_info)
    """
    if not filename:
        return False, "Filename cannot be empty", {}

    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '.{ext}'. Supported types: PDF, DOCX, XLSX, TXT, PNG, JPG, JPEG.", {}

    size = len(file_bytes)
    if size == 0:
        return False, "Uploaded file is empty (0 bytes).", {}

    if size > MAX_FILE_SIZE_BYTES:
        return False, f"File size exceeds maximum limit of 25MB (File size: {size / (1024*1024):.2f}MB).", {}

    file_info = {
        "extension": ext,
        "mime_type": ALLOWED_EXTENSIONS[ext],
        "size_bytes": size,
        "is_image": ext in ['png', 'jpg', 'jpeg'],
        "is_pdf": ext == 'pdf',
        "is_docx": ext == 'docx',
        "is_xlsx": ext == 'xlsx',
        "is_txt": ext == 'txt'
    }

    return True, "", file_info
