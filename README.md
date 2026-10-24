# ReceiptReader · Day 17/100

**Review-first receipt OCR and key-information extraction (KIE)** · Python 3.11 · Tesseract · Streamlit · research archive v10

> **Status (2026-10-24):** The locally demonstrated application runs **Tesseract PSM 6 + transparent field heuristics**, offers editable `company`, `date`, `address`, and `total`, and requires user confirmation before JSON/CSV export. **The v10 research pipeline has NOT been integrated into the running application.** Research results in `reports/` are not app accuracy measurements.

[Dokumentasi lengkap Bahasa Indonesia](docs/id/README.md) · [Complete English documentation](docs/en/README.md) · [Engineering/AI agent contract](AGENTS.md) · [GitHub](https://github.com/MENSTRUE/ReceiptReader)

## The problem & product promise

Receipt transcription is repetitive and error-prone, especially for merchant names, dates, multi-line addresses, and payment totals. The app accepts a PNG/JPG/WEBP image, performs OCR, **suggests** four fields, reveals the raw OCR text, and requires a human to check and correct them before export. It is a document-assistance prototype, **not** autonomous bookkeeping, financial reconciliation, or a production-grade accounting tool.

### Before → Now → Next

| Phase | Evidence-based status |
|---|---|
| **Before: research** | SROIE and CORD v2 exploratory OCR/KIE research through v10. Split audit, model selection and evaluation files are in `reports/`; notebook at `notebooks/receiptreader.ipynb`. |
| **Now: operational MVP** | Windows Tesseract baseline, 4 editable fields, mandatory confirmation, JSON/CSV export. A local **single synthetic/example receipt image** was observed extracting `TOKO MAJU JAYA`, `2025-04-12`, `Jl. Melati No. 123…`, `241980`. This is a smoke test, **not an accuracy statistic**, and its screenshot is not verified in the remote repository. |
| **Next: evidence parity** | Audit v10 archive/model type and notebook; reproduce preprocessing, run repeatable frozen-image parity tests; expand representative manually verified receipts; improve failure/rejection handling; deploy only with privacy safeguards. |

## Getting started · Windows PowerShell

```powershell
cd "D:\porto\100 day\day 17\ReceiptReader"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
winget install --id UB-Mannheim.TesseractOCR -e
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`. Tesseract is a **separate system executable**; `pip install pytesseract` alone will not install it. If Tesseract is not on PATH, set its command in `src/receiptreader/ocr.py` or use the installed, locally tested version that auto-detects Windows paths. **GitHub `main` was observed still containing the original short `ocr.py`; local edits may be ahead of remote.**

### App workflow / kontrak output

`Image → EXIF orientation + grayscale/contrast → Tesseract PSM 6 → text heuristics → editable fields → human confirmation → JSON/CSV`.

| Field | Example | Notes |
|---|---|---|
| `company` | `TOKO MAJU JAYA` | Merchant candidate; verify especially for logos/headers |
| `date` | `2025-04-12` | ISO format if recognized; ambiguous date conventions require review |
| `address` | `Jl. Melati No. 123, ...` | Optional, may be incomplete/absent; do not hallucinate missing words |
| `total` | `241980` | Monetary **string**; check currency, separators, taxes, tendered amount and change |

A successful OCR read is **not** a validated receipt. The `verified_by_user` flag means the user confirmed the values; it is not a machine accuracy label. Never export unconfirmed values as authoritative.

## Research datasets and traceability

| Source | Role | What it supports / does not support |
|---|---|---|
| **SROIE (ICDAR 2019)** | Main receipt KIE research: company/date/address/total | Malaysian receipts, different currency/domain from Indonesian demo. Audit reports: SROIE train 626; internal train 501, validation 125; published test 361, 8 image hashes overlap, repeated hash-clean test 353. Source: [ICDAR 2019 SROIE competition](https://rrc.cvc.uab.es/?ch=13). |
| **CORD v2 (NAVER Clova)** | Supplementary total-amount supervision in research | Indonesian receipt structure, but `gt_parse` is **not** equivalent company/date/address gold. Official train 800; do not treat it as four-field complete ground truth. [CORD v2 on Hugging Face](https://huggingface.co/datasets/naver-clova-ix/cord-v2). |
| **Illustrative demo receipt** | Local UI/OCR smoke test | Example receipt; does **not** constitute held-out evaluation, real transaction evidence, or generalization performance. |

**Availability/license:** Check each dataset's original rights, usage terms, revisions and redistribution constraints. The MIT code license **does not license third-party receipt images, annotations, models or personal data**. Do not commit raw receipts, private annotations, Kaggle uploads, credentials or unlicensed training corpora.

## Measured research evidence — do not collapse protocols

These numbers are read from the repository's `reports/v10_summary.json` and `reports/split_audit.json` and apply to research v10 **only**:

| v10 research protocol | N | Company exact | Date exact | Address exact | Total exact | Macro exact | Four of four exact |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Repeated image/pixel SROIE test** (previously inspected; non-independent) | 80 | 52.50% | 75.00% | 36.25% | 55.00% | 54.6875% | 5.00% |

Other reported validation metrics are **distinct experiments**: SROIE validation total exact **80.8% → 82.4%** with CORD augmentation; `reports/v10_summary.json` also records **95% CORD validation total exact** under its own protocol. Neither is the live app's total accuracy. Some experiments repeatedly inspected the published test; do **not** call them untouched held-out test results. See `reports/v10_repeated_pixel_metrics.json`, `reports/v10_frozen_selection.json`, and `reports/total_comparison_validation.json` for configurations and supporting evidence.

### Evaluation and audit checklist

1. Define one target per source; reject conflation of OCR transcript accuracy, individual field exact match, and full-receipt exact match.
2. Hash/deduplicate source images **before** splits; maintain source, image ID, protocol, split, annotation coverage and preprocessing version.
3. Freeze training/validation/test before tuning. A test reused to revise rules becomes **repeated diagnostic**, not untouched evaluation.
4. Report exact-match per field, macro exact, all-four exact, sample count, failure count, confidence interval when warranted, image/annotated-text protocol, and source-specific cases.
5. Separate model selection on validation from external domain/generalization checks; log error examples with permission and redaction.
6. Do not promote one fabricated example, template smoke test or corrected form values into accuracy metrics.

## Repository map

```text
ReceiptReader/
├── app/streamlit_app.py       # Streamlit review-first UI
├── src/receiptreader/         # preprocessing, OCR, extraction, inference, schemas
├── tests/test_extraction.py   # current tests (audit against recent local extractor changes)
├── notebooks/receiptreader.ipynb
├── reports/                   # measured v10 research JSON/CSV, see reports/README.md
├── assets/plots/              # committed research plots
├── assets/screenshots/        # real app screenshot evidence; currently no verified screenshot
├── models/                    # README only until research model integration verified
├── exports/                   # ignored, local reviewed JSON/CSV only
├── scripts/check_environment.py
├── docs/id/README.md          # Indonesian project reference
├── docs/en/README.md          # English project reference
├── pass/README.md             # access practices only, NEVER secrets
├── AGENTS.md                  # coding agents and scientific claims contract
├── requirements.txt · pytest.ini · .gitignore · LICENSE
└── README.md
```

**Do not introduce non-existent paths to imply finished features.** Some locally tested extractor/Tesseract edits may not yet be in the GitHub branch; compare `git status`/`git diff` before claiming remote parity.

## Evidence assets & publication checklist

| Asset | Present in remote tree? | Allowed claim |
|---|---|---|
| `assets/plots/01_partitions.png` | Yes | Research data partitions, after checking plot labels |
| `assets/plots/v10_comparison.png` | Yes | Research v10 comparison, with correct repeated-test qualifier |
| `reports/*.json`, selected `*.csv` | Yes | The exact per-file protocol and aggregates only |
| `assets/screenshots/` real uploaded receipt UI screenshot | Not verified | Add an authentic sanitized app screenshot and caption it *demo*, not evaluation |
| `exports/receipt_reviewed.csv` or `.json` | Locally generated only; Gitignored | Only export after checkbox + confirmation. Do not commit personally identifying receipts |
| v10 trained model binary | **Not verified/integrated** | Do not claim model weights or research pipeline power the app |

Recommended authentic evidence: screenshot of the actual review form (with redacted details), screenshot of an OCR failure/blank field, existing research plot with documented protocol, and a small **hand-checked synthetic fixture CSV** explicitly labelled `demo_fixture` rather than test performance. If contributing anonymized fixture CSV, include source rights and expected fields; do not publish raw real receipts.

## Limitations / boundaries

The four-field demonstration on one example does not establish cross-store accuracy. OCR may miss characters, currencies and context; heuristics can confuse subtotal, paid amount and final total; addresses are especially challenging. Domain/language differences between SROIE and Indonesian receipts may reduce transfer. Baseline Tesseract is **not** v10. Not suitable for autonomous payment, tax compliance, fraud determination or bookkeeping. Keep a manual correction and reject path. Consent, image retention, secure server deployment and file size limits need review before exposure to real users.

## Testing, deployment, troubleshooting

Run `python -m pytest -q` using the project `.venv`, then smoke test **upload → OCR → edit → verify → export** with a licensed/synthetic sample. Note: the remote `tests/test_extraction.py` was authored against an earlier output format (`12/10/2026`); after normalizing dates to ISO, update this test deliberately rather than blindly relying on old results. Production/cloud deployment also requires a Tesseract binary in the environment, resource limits, explicit data retention policy and TLS. No public hosted deployment has been verified.

| Symptom | Likely issue / fix |
|---|---|
| `TesseractNotFoundError` | Binary missing; install Windows Tesseract and configure executable path |
| `Error opening data file ...` | Requested `ind` language pack not installed; inspect `tesseract --list-langs`, use installed `eng` for baseline |
| Incorrect `total` (paid amount) | Inspect raw OCR, label exclusions and line grouping; do not select last number by default |
| Empty `address` | OCR starts with stray character or misses street prefix; inspect raw text and correct manually |
| Tests fail after date normalization | Refresh fixture expectations to ISO and add regression tests |
| `ModuleNotFoundError: receiptreader` | Run from repository root and use provided `pytest.ini` and application path setup |
| Stale field values after changing upload | Re-run OCR and verify that session state corresponds to current file; filename-only identity is a known potential bug |

## FAQ

**Is this AI?** OCR and extraction is document automation; the current running implementation is Tesseract plus rules. Research v10 is distinct, not yet integrated.

**Is 4/4 on the example 100% accuracy?** No. It is one smoke case with known fields; no independently sampled benchmark of the app has been done.

**Is the model trained on CORD for four fields?** No; CORD label semantics differ, especially for company/date/address.

**Can I use this for financial records?** Only after independently verifying all extracted values; deployment, privacy and accuracy validation remain open.

**Why keep raw OCR visible?** To let users inspect source evidence, trace mistakes and correct fields rather than accept unsupported guesses.

## License and attribution

Project source: **MIT** — see [LICENSE](LICENSE). Dataset licenses, image rights and third-party OCR/model dependencies are independent. Attribute SROIE/ICDAR, CORD/NAVER, Tesseract and any actual asset contributors according to their own requirements. Research figures must retain protocol captions and provenance.

**Contribution standard:** reproducible instructions, tests, safe handling of receipt images, small scoped commits and truthful results. Open a PR with a before/after note and matching bilingual documentation changes.
