import re
from .schemas import ReceiptFields

DATE_RE = re.compile(r'\b(?:[0-3]?\d[-/][01]?\d[-/]20\d{2}|20\d{2}[-/][01]?\d[-/][0-3]?\d)\b')
PRICE_RE = re.compile(r'(?:RM|RP|IDR|\$)?\s*([0-9][0-9., ]*[0-9]|[0-9])\s*$', re.I)
TOTAL_RE = re.compile(r'\b(?:grand\s*total|total\s*(?:due|amount|bayar)?|jumlah\s*(?:bayar|akhir)?)\b', re.I)


def candidate_fields(raw_text: str) -> ReceiptFields:
    """Transparent heuristic guesses only; address deliberately left for manual correction."""
    lines = [x.strip() for x in raw_text.splitlines() if x.strip()]
    company = lines[0][:120] if lines else ''
    date = next((m.group(0) for line in lines if (m := DATE_RE.search(line))), '')
    total = ''
    for line in reversed(lines):
        if TOTAL_RE.search(line):
            numbers = PRICE_RE.search(line)
            if numbers:
                total = numbers.group(1).strip()
                break
    return ReceiptFields(company=company, date=date, address='', total=total)
