# ReceiptReader — English documentation

**Problem:** Manual receipt transcription is tedious while OCR often misreads merchant, date, address and total. ReceiptReader offers editable field suggestions and requires explicit human verification before exporting.

**Current implementation:** Tesseract OCR plus simple heuristics; experimental v10 artifacts are NOT yet integrated. Address is blank by default because historical address-field performance was weak. This scaffold has no measured model accuracy.

**Workflow:** upload → orientation/contrast preprocessing → OCR → field candidates → manual correction → confirmation → JSON/CSV.

**Getting started:** follow the root README; Tesseract binary is a system requirement beyond pip. `src/receiptreader` is independent of the Streamlit UI.

**Data:** SROIE and CORD v2 have different annotation protocols; using CORD does not supply missing company/date/address labels. Do not redistribute third-party receipt images without permission.

**Next:** inspect and verify v10 files and dependencies; ensure exact preprocessing and inference parity on a fixed image set, then integrate only verified components. Preserve correction and privacy safeguards.
