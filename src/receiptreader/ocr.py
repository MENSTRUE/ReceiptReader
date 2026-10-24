
import os
import shutil
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps


class OCRUnavailable(RuntimeError):
    """Raised when the Tesseract OCR engine is unavailable."""


def configure_tesseract() -> str:
    """
    Locate and configure the Tesseract executable.

    Supports Windows installation paths, environment
    variables, and operating-system PATH.
    """
    candidates = []

    custom_path = os.environ.get("TESSERACT_CMD")

    if custom_path:
        candidates.append(custom_path)

    # Common Windows installation paths
    if os.name == "nt":
        candidates.extend([
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ])

    # Detect executable through PATH
    detected = shutil.which("tesseract")

    if detected:
        candidates.append(detected)

    for candidate in candidates:
        executable = Path(candidate)

        if not executable.is_file():
            continue

        try:
            result = subprocess.run(
                [str(executable), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0:
                pytesseract.pytesseract.tesseract_cmd = str(
                    executable
                )
                return str(executable)

        except (OSError, subprocess.TimeoutExpired):
            continue

    raise OCRUnavailable(
        "Tesseract OCR executable was not found. "
        "Install it using: "
        "winget install --id UB-Mannheim.TesseractOCR -e "
        "or set the TESSERACT_CMD environment variable."
    )


def get_available_languages() -> list[str]:
    """Return the installed Tesseract language packs."""
    configure_tesseract()

    try:
        return pytesseract.get_languages(config="")
    except (
        pytesseract.TesseractNotFoundError,
        pytesseract.TesseractError,
        OSError,
    ) as exc:
        raise OCRUnavailable(
            f"Unable to read OCR languages: {exc}"
        ) from exc


def extract_text(
    image: Image.Image,
    lang: str = "eng",
) -> str:
    """
    Extract receipt text using Tesseract PSM 6.

    This is a baseline OCR implementation.
    It does not invoke the research v10 pipeline.

    Args:
        image: Pillow image.
        lang: Tesseract language code, e.g. eng, ind.

    Returns:
        OCR text as a UTF-8 Python string.
    """
    configure_tesseract()

    if image is None:
        raise ValueError("Image cannot be None.")

    if not isinstance(image, Image.Image):
        raise TypeError(
            "Expected a PIL.Image.Image instance."
        )

    # Correct EXIF orientation
    processed = ImageOps.exif_transpose(image)

    # RGB conversion for consistent OCR
    processed = processed.convert("RGB")

    # Avoid silently requesting unavailable language packs
    available = get_available_languages()

    requested = lang.split("+")

    missing = [
        code
        for code in requested
        if code not in available
    ]

    if missing:
        raise OCRUnavailable(
            f"Language pack unavailable: {missing}. "
            f"Installed languages: {available}"
        )

    try:
        text = pytesseract.image_to_string(
            processed,
            lang=lang,
            config="--oem 3 --psm 6",
        )

        return text.strip()

    except (
        pytesseract.TesseractNotFoundError,
        pytesseract.TesseractError,
        OSError,
    ) as exc:
        raise OCRUnavailable(
            f"Tesseract OCR failed: {exc}"
        ) from exc
