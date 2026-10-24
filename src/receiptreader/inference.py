from PIL import Image
from .preprocessing import prepare_image
from .ocr import extract_text
from .extraction import candidate_fields

def analyze(image: Image.Image) -> tuple[str, dict]:
    """Baseline OCR and heuristics. Model v10 needs separate artifact audit before wiring."""
    text = extract_text(prepare_image(image))
    return text, candidate_fields(text).to_dict()
