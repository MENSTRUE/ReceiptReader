import pytesseract
from PIL import Image

class OCRUnavailable(RuntimeError):
    pass

def extract_text(image: Image.Image, lang: str = 'eng') -> str:
    """Tesseract PSM 6 baseline. Does NOT invoke research v10 pipelines."""
    try:
        return pytesseract.image_to_string(image, lang=lang, config='--psm 6')
    except (pytesseract.TesseractNotFoundError, pytesseract.TesseractError) as exc:
        raise OCRUnavailable(f'Tesseract OCR unavailable: {exc}') from exc
