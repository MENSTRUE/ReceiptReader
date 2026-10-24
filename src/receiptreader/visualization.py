from PIL import Image

def make_preview(image: Image.Image) -> Image.Image:
    preview=image.copy()
    preview.thumbnail((900,1100))
    return preview
