from PIL import Image, ImageOps, ImageEnhance

def prepare_image(image: Image.Image) -> Image.Image:
    """Explicit, reversible-independent OCR preprocessing baseline."""
    im = ImageOps.exif_transpose(image).convert('RGB')
    im = ImageOps.grayscale(im)
    return ImageEnhance.Contrast(im).enhance(1.5)
