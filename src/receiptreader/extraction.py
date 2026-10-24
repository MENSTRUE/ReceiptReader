
import re
from datetime import datetime

from .schemas import ReceiptFields


"""
ReceiptReader — Baseline Field Extraction

Pipeline:
    Tesseract OCR text
        -> Text normalization
        -> Merchant extraction
        -> Date extraction
        -> Address extraction
        -> Total extraction
        -> ReceiptFields

Important:
    - Research v10 pipeline is NOT integrated.
    - Results are heuristic candidates.
    - Human verification is required.
"""


# ============================================================
# 1. DATE PATTERNS
# ============================================================

MONTHS = {
    "jan": 1,
    "januari": 1,
    "january": 1,
    "feb": 2,
    "februari": 2,
    "february": 2,
    "mar": 3,
    "maret": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "mei": 5,
    "may": 5,
    "jun": 6,
    "juni": 6,
    "june": 6,
    "jul": 7,
    "juli": 7,
    "july": 7,
    "agu": 8,
    "agt": 8,
    "agustus": 8,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "okt": 10,
    "oct": 10,
    "oktober": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "des": 12,
    "dec": 12,
    "desember": 12,
    "december": 12,
}

MONTH_PATTERN = "|".join(
    sorted(map(re.escape, MONTHS), key=len, reverse=True)
)

TEXT_DATE_RE = re.compile(
    rf"\b(\d{{1,2}})\s+({MONTH_PATTERN})\.?[\s,/-]+(\d{{4}})\b",
    re.IGNORECASE,
)

NUMERIC_DATE_RE = re.compile(
    r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}"
    r"|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b"
)

DATE_LABEL_RE = re.compile(
    r"\b(?:tanggal|tgl|date)\b",
    re.IGNORECASE,
)


# ============================================================
# 2. ADDRESS PATTERNS
# ============================================================

ADDRESS_START_RE = re.compile(
    r"^(?:"
    r"jl\.?|jln\.?|jalan|"
    r"street|st\.?|road|rd\.?|"
    r"alamat\s*:?"
    r")(?=\s|$)",
    re.IGNORECASE,
)

ADDRESS_CONTINUATION_RE = re.compile(
    r"\b(?:"
    r"kel\.?|kelurahan|"
    r"kec\.?|kecamatan|"
    r"kab\.?|kabupaten|kota|"
    r"jakarta|bandung|surabaya|semarang|"
    r"yogyakarta|depok|bekasi|tangerang|"
    r"indonesia"
    r")\b",
    re.IGNORECASE,
)

POSTAL_CODE_RE = re.compile(r"\b\d{5}\b")

PHONE_RE = re.compile(
    r"^(?:telp?\.?|telepon|phone|hp|whatsapp|wa)"
    r"(?=\s|:|\.|$)",
    re.IGNORECASE,
)

HEADER_STOP_RE = re.compile(
    r"^(?:tanggal|tgl|date|time|waktu|"
    r"no\.?\s*(?:nota|struk|transaksi)|"
    r"receipt|invoice|kasir|cashier|shift|"
    r"qty|nama\s+barang|subtotal|total)"
    r"\b",
    re.IGNORECASE,
)

SEPARATOR_RE = re.compile(r"^[-=_.\s*]{3,}$")


# ============================================================
# 3. TOTAL / CURRENCY PATTERNS
# ============================================================

TOTAL_LABEL_RE = re.compile(
    r"\b(?:"
    r"grand\s+total|"
    r"total\s+(?:belanja|akhir|tagihan)|"
    r"total|"
    r"amount\s+due|"
    r"net\s+amount|"
    r"jumlah\s+(?:tagihan|belanja)"
    r")\b",
    re.IGNORECASE,
)

EXCLUDED_TOTAL_RE = re.compile(
    r"\b(?:"
    r"subtotal|sub\s+total|"
    r"diskon|discount|"
    r"pajak|tax|ppn|dpp|"
    r"kembalian|kembali|change|"
    r"tunai|cash|payment|"
    r"jumlah\s+bayar|uang\s+bayar|"
    r"dibayar|bayar\s+tunai|tendered"
    r")\b",
    re.IGNORECASE,
)

AMOUNT_RE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?:Rp\.?\s*|IDR\s*|RM\s*)?"
    r"(-?\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{2})?"
    r"|-?\d+[.,]\d{2}"
    r"|-?\d+)"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)


# ============================================================
# 4. TEXT NORMALIZATION
# ============================================================

def _clean_line(value: str) -> str:
    """Normalize whitespace without changing text meaning."""
    return " ".join(str(value).split()).strip()


def _normalize_ocr_line(value: str) -> str:
    """
    Remove a single stray OCR character before known labels.

    Examples:
        '1 Jl. Melati No. 123'
            -> 'Jl. Melati No. 123'

        'z Telp. (021) 7654 3210'
            -> 'Telp. (021) 7654 3210'

        'Tanggal : 12 Apr 2025'
            -> unchanged
    """
    line = _clean_line(value)

    # Require an actual whitespace boundary before the label.
    # Avoid removing the beginning of ordinary merchant names.
    line = re.sub(
        r"^[A-Za-z0-9]\s+(?="
        r"(?:Tanggal|Total|Jl\.?|Jln\.?|Jalan|"
        r"Alamat|Telp\.?|Telepon)"
        r"(?=\s|:|\.|$))",
        "",
        line,
        flags=re.IGNORECASE,
    )

    return line


def _prepare_lines(raw_text: str) -> list[str]:
    """Prepare OCR lines for deterministic extraction."""
    return [
        normalized
        for raw in raw_text.splitlines()
        if (normalized := _normalize_ocr_line(raw))
        and not SEPARATOR_RE.fullmatch(normalized)
    ]


# ============================================================
# 5. COMPANY / MERCHANT
# ============================================================

def extract_company(lines: list[str]) -> str:
    """Choose a plausible merchant name near the receipt top."""
    for line in lines[:8]:

        if HEADER_STOP_RE.search(line):
            continue

        if ADDRESS_START_RE.search(line):
            continue

        if PHONE_RE.search(line):
            continue

        if POSTAL_CODE_RE.search(line):
            continue

        if len(line) < 3:
            continue

        return line[:120]

    return ""


# ============================================================
# 6. DATE
# ============================================================

def _parse_date(value: str) -> str:
    """Return an ISO date when a recognized valid date exists."""
    text_match = TEXT_DATE_RE.search(value)

    if text_match:
        day = int(text_match.group(1))
        month_name = text_match.group(2).lower()
        year = int(text_match.group(3))
        month = MONTHS.get(month_name)

        if month is not None:
            try:
                return datetime(
                    year, month, day
                ).strftime("%Y-%m-%d")
            except ValueError:
                pass

    numeric_match = NUMERIC_DATE_RE.search(value)

    if numeric_match:
        date_text = numeric_match.group()

        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
        ):
            try:
                return datetime.strptime(
                    date_text, fmt
                ).strftime("%Y-%m-%d")
            except ValueError:
                continue

    return ""


def extract_date(lines: list[str]) -> str:
    """Prioritize labeled date lines."""
    preferred = [
        line for line in lines
        if DATE_LABEL_RE.search(line)
    ]

    remaining = [
        line for line in lines
        if not DATE_LABEL_RE.search(line)
    ]

    for line in preferred + remaining:
        date = _parse_date(line)

        if date:
            return date

    return ""


# ============================================================
# 7. ADDRESS
# ============================================================

def _is_address_start(line: str) -> bool:
    return bool(ADDRESS_START_RE.search(line))


def _is_address_continuation(line: str) -> bool:
    return bool(
        ADDRESS_CONTINUATION_RE.search(line)
        or POSTAL_CODE_RE.search(line)
    )


def extract_address(lines: list[str]) -> str:
    """
    Extract a possible postal address from receipt header.

    Addresses are not guaranteed to be correct.
    The app must keep the field editable.
    """
    start_index = None

    for index, line in enumerate(lines[:15]):
        if _is_address_start(line):
            start_index = index
            break

    if start_index is None:
        return ""

    address_lines = []

    for line in lines[start_index:start_index + 5]:

        if HEADER_STOP_RE.search(line):
            break

        if PHONE_RE.search(line):
            break

        if SEPARATOR_RE.fullmatch(line):
            break

        if not address_lines:
            address_lines.append(line)
            continue

        if _is_address_continuation(line):
            address_lines.append(line)
        else:
            break

    return ", ".join(address_lines)[:300]


# ============================================================
# 8. MONEY NORMALIZATION
# ============================================================

def _normalize_amount(value: str) -> str:
    """Normalize conventional currency values to plain numbers."""
    text = value.strip().replace(" ", "")

    if not text:
        return ""

    negative = text.startswith("-")
    number = text.lstrip("-")

    if "." in number and "," in number:
        if number.rfind(".") > number.rfind(","):
            number = number.replace(",", "")
        else:
            number = number.replace(".", "").replace(",", ".")

    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", number):
        number = number.replace(".", "")

    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", number):
        number = number.replace(",", "")

    elif re.fullmatch(r"\d+[.,]\d{2}", number):
        number = number.replace(",", ".")

    elif not number.isdigit():
        return ""

    return ("-" if negative else "") + number


def _amounts_after_total_label(line: str) -> list[str]:
    match = TOTAL_LABEL_RE.search(line)

    if match is None:
        return []

    remainder = line[match.end():]

    amounts = []

    for found in AMOUNT_RE.finditer(remainder):
        amount = _normalize_amount(found.group(1))

        if amount:
            amounts.append(amount)

    return amounts


# ============================================================
# 9. TOTAL
# ============================================================

def extract_total(lines: list[str]) -> str:
    """
    Extract total payable amount without confusing it with
    subtotal, taxes, payment, or change.

    When equally plausible totals disagree, return an
    empty candidate rather than inventing a value.
    """
    candidates = []

    for line in lines:

        if EXCLUDED_TOTAL_RE.search(line):
            continue

        label_match = TOTAL_LABEL_RE.search(line)

        if label_match is None:
            continue

        amounts = _amounts_after_total_label(line)

        if not amounts:
            continue

        label = label_match.group(0).lower()

        priority = (
            3 if (
                "grand" in label
                or "belanja" in label
                or "akhir" in label
                or "tagihan" in label
            )
            else 2
        )

        candidates.append(
            (priority, amounts[-1])
        )

    if not candidates:
        return ""

    best_priority = max(
        priority for priority, _ in candidates
    )

    best_values = {
        amount
        for priority, amount in candidates
        if priority == best_priority
    }

    if len(best_values) != 1:
        return ""

    return next(iter(best_values))


# ============================================================
# 10. MAIN EXTRACTION API
# ============================================================

def candidate_fields(raw_text: str) -> ReceiptFields:
    """
    Extract candidate fields from Tesseract OCR output.

    Output:
        ReceiptFields(
            company=...,
            date=...,
            address=...,
            total=...
        )

    This remains a heuristic baseline, not research v10.
    All suggested fields require human verification.
    """
    if not raw_text or not raw_text.strip():
        return ReceiptFields(
            company="",
            date="",
            address="",
            total="",
        )

    lines = _prepare_lines(raw_text)

    return ReceiptFields(
        company=extract_company(lines),
        date=extract_date(lines),
        address=extract_address(lines),
        total=extract_total(lines),
    )
