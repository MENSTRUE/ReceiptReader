# ReceiptReader — Complete English Documentation

**Day 17/100 | Human-verified receipt OCR and information extraction**

[Root README](../../README.md) · [Bahasa Indonesia](../id/README.md) · [Engineering contract](../../AGENTS.md) · [Repository](https://github.com/MENSTRUE/ReceiptReader)

## Executive summary

ReceiptReader helps users transcribe **merchant/company, date, address and total** from a receipt image. OCR produces suggestions, and a user edits and confirms them before exporting CSV or JSON. The product is a prototype for human-assisted document processing, not an autonomous financial system.

**Evidence-backed current status (October 24, 2026):** a local screenshot demonstrates all four fields on **one illustrative receipt**. The audited GitHub application uses **Tesseract PSM 6 + field heuristics**, **not** the v10 research inference. No independent app-wide accuracy metric exists. A one-image successful demo must never be advertised as 100% accuracy.

## Before → Now → Next

| Stage | Description | Evidence |
|---|---|---|
| **Before** | Research on Malaysian SROIE receipts and Indonesian CORD v2, culminating in experimental v10 | `notebooks/receiptreader.ipynb`, `reports/` |
| **Now** | Runnable Streamlit upload/preview/OCR/edit/confirm/export; four editable fields | `app/streamlit_app.py`, `src/receiptreader/`; local smoke screenshot not yet verified as committed |
| **Next** | Inspect the actual v10 assets, build a parity harness, add licensed independently annotated receipts, strengthen security and evaluate transfer | Planned; not completed |

## Problem statement, users and acceptance criteria

The intended users are small businesses and administrators who enter receipt data. The problem is repetitive transcription and occasional OCR error. Success is not merely returning non-empty fields: the user must be able to inspect the original image and raw OCR text, correct all four values and deliberately approve the export. Mistaking the amount paid for the actual total or inventing a missing street address violates the purpose of the product.

## Runtime architecture

```text
PNG/JPEG/WEBP receipt
   -> PIL decode, EXIF orientation, grayscale/contrast
   -> Tesseract PSM 6 OCR (default: eng)
   -> raw text
   -> deterministic date / address / merchant / total extraction
   -> user-editable four-field form
   -> explicit verification checkbox + confirm
   -> local CSV / JSON download
```

The app owns UI state, `preprocessing.py` owns image transforms, `ocr.py` calls an installed system OCR binary, `extraction.py` produces rule-based candidates, `inference.py` orchestrates the pipeline, and `schemas.py` defines output fields. Numeric amounts remain strings, because locale/decimal/currency interpretation has not been generalized.

## Local setup (Windows 11 / PowerShell)

```powershell
cd "D:\porto\100 day\day 17\ReceiptReader"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
winget install --id UB-Mannheim.TesseractOCR -e
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`. Installing `pytesseract` with pip does **not** install Tesseract itself. Check language availability using `tesseract --list-langs`. If a local Windows auto-configuration change is not yet committed, GitHub's `ocr.py` can still differ from the local version. Verify the diff before asserting environment parity.

## Data contract and actual illustrative example

| Output key | Example from local smoke | Risk |
|---|---|---|
| `company` | `TOKO MAJU JAYA` | Header/logotype confusion |
| `date` | `2025-04-12` | Ambiguous date order or wrong OCR segment |
| `address` | `Jl. Melati No. 123, Kel. Sukamaju, Kec. Cilandak, Jakarta Selatan 12450` | Missing street prefix, multiline grouping, hallucination risk |
| `total` | `241980` | Subtotal vs grand total vs amount paid (`250000`) vs change (`8020`) |

These outputs are **illustrative smoke-case targets**. They are not independent ground truth labels from a receipt test cohort and must not be counted as model benchmark accuracy.

## Dataset provenance and rights

**SROIE — ICDAR 2019:** [competition source](https://rrc.cvc.uab.es/?ch=13). Its Malaysian receipt labels map to company, date, address and total research targets. The committed split audit reports 626 training receipts, split internally into 501 train and 125 validation; published test has 361 images, with eight overlapping hashes excluded for a 353-image repeated hash-clean diagnostic. **The test data were inspected during research** and are not a pristine untouched final test.

**CORD v2 — NAVER Clova:** [dataset source](https://huggingface.co/datasets/naver-clova-ix/cord-v2). The repository audit lists 800 official training receipts. CORD provides richer parsed receipt sections but does **not** supply equivalent labels for all SROIE company/date/address targets. The v10 supplementary experiment targets **total**; do not extrapolate its score to four-field KIE.

**Illustrative UI receipt:** sample image used for local demo only, not an independently collected real receipt or cross-domain test. Third-party images, labels and model assets must obey their original licenses and distribution restrictions. Code MIT does not grant rights to them. Receipt photos may contain personal information; protect, redact and avoid committing such files.

## Measured research results and protocol boundaries

| Protocol | N | Company | Date | Address | Total | Mean of four exact | All four correct |
|---|---:|---:|---:|---:|---:|---:|---:|
| v10 repeated SROIE **image/pixel** diagnostic, previously inspected | 80 | 52.50% | 75.00% | 36.25% | 55.00% | 54.6875% | 5.00% |

Values above come from `reports/v10_repeated_pixel_metrics.json`; the `baseline` and `v10` entries are **identical** in that report. Do not claim improvement on this cohort. `reports/total_comparison_validation.json` separately reports **80.8% SROIE validation total exact** for SROIE-only and **82.4%** for CORD-augmented. `reports/v10_summary.json` additionally reports **95% CORD validation total exact** under its **distinct** evaluation setup. These are neither app inference accuracy nor a four-field success rate.

Test reuse, annotated-text protocols vs raw-pixel OCR, differences in label availability and domain shift must always be named. A false comparison between these figures is a scientific reporting error.

### Auditing and reproducibility

- Record the dataset version, original location, license, hashes, receipt identifiers, split assignment and label coverage before training.
- Freeze validation and test selection; if test examples have influenced fixes, mark them as repeated diagnostics.
- Store evaluation inputs, OCR configuration (language/PSM/engine), preprocessing parameters, candidate extractor version, failure count, predictions and normalization semantics.
- Report exact match per field, macro exact, all-four match, sample N and confidence intervals only where actually computed.
- For v10 integration, inspect original binary/checkpoint or heuristic model selection, reproduce original notebook outputs on identical image bytes and assert field-level parity before switching the app label.

## Evidence assets and publication

`assets/plots/01_partitions.png` and `assets/plots/v10_comparison.png` are committed research figures. Cite their research protocol; do not misrepresent them as live app evaluation. JSON/CSV in `reports/` must remain associated with their source and sample count. `assets/screenshots/` was observed without a committed screenshot at the time of audit; add authentic **redacted** app screenshots such as `01_upload.png`, `02_review_fields.png`, and `03_export.png`, with captions identifying them as **demo images**. Do not invent screenshot performance dashboards.

`exports/` is local and Gitignored: store reviewed JSON and CSV there only when the user explicitly chooses. If you publish synthetic fixture CSV, mark it clearly as `demo_fixture`, provide a verifiable source/rights and refrain from treating it as independent validation. Never commit sensitive transaction information.

## Repository map and change policy

See [root repository map](../../README.md#repository-map). The main areas are `app/`, `src/receiptreader/`, `tests/`, `notebooks/`, `reports/`, `models/`, `assets/plots/`, `assets/screenshots/`, `exports/`, `scripts/`, `pass/`, and `docs/`. `models/README.md` explicitly says the app has no verified v10 model binary. `pass/README.md` is access guidance only, never a place to store keys or passwords. The full engineering rules are in `AGENTS.md`.

## Claim boundaries / limitations

- Current working inference = baseline Tesseract + regex/rule extraction; not validated v10.
- A correct demonstration on a single sample does not yield population accuracy.
- SROIE and CORD cover different countries, labels and financial notation.
- OCR is vulnerable to lighting, skew, poor contrast, crumpled paper, low resolution and handwritten fields.
- Address reconstruction is a known weak research area; avoid inventing unseen words.
- Monetary values can be dangerously confused with subtotal, payment or change.
- User confirmation signifies user responsibility, not independently verified annotation.
- Public deployment requires security, privacy, retention and real-use evaluation that have **not been verified**.

## Testing and deployment plan

For each change run Python 3.11 tests and a single licensed image-to-export smoke. Document the Tesseract binary/version as an external dependency. The current remote `tests/test_extraction.py` asserts a **legacy date format** (`12/10/2026`), while locally demonstrated extractor changes normalize to ISO; update fixtures to an agreed output contract and run tests again before describing them as passing. Add regression tests for street prefixes, date parsing, payment-vs-total separation, invalid images, empty fields, changing uploads and session identity using the file content hash.

Deployment beyond localhost requires installing the Tesseract binary, limiting pixel count and file size, TLS, access restrictions, no PII telemetry, retention/deletion rules, and resource controls. No deployed public endpoint has been verified.

## Troubleshooting

| Symptom | Investigation |
|---|---|
| `TesseractNotFoundError` | Install Windows Tesseract and configure `tesseract.exe` path |
| `ind.traineddata` unavailable | Inspect installed languages; use `eng` only if acceptable and explicitly documented |
| Empty date | Confirm OCR text contains a recognized textual/numeric date; inspect normalization |
| Empty address | Check OCR prefix noise (`1 Jl.`) and multi-line grouping; keep manual editing |
| Wrong total | Inspect `Total` vs `Subtotal`, `Jumlah Bayar`, PPN, and change |
| Tests changed unexpectedly | Compare local and remote `extraction.py`, update test expectation deliberately |
| Old fields after new upload | Reset session review state based on content hash, not only filename; this is a recommended fix |

## Roadmap

**P0:** reconcile local vs GitHub, update tests, harden session state and sanitize screenshots. **P1:** v10 artifact provenance/hash and reproducible parity tests. **P2:** licensed real Indonesian receipts with independent annotations, uncertainty/rejection policy and per-store metrics. **P3:** privacy-reviewed controlled deployment and documentation of operational limits.

## FAQ

**Does it use a trained deep learning model?** Not in the currently running app. The research pipeline and its actual artifacts must be audited before integration.

**Is the screenshot evidence of 100% accuracy?** No: one constructed example was tested, not a representative benchmark.

**Can I rely on the numbers for taxes or refunds?** Only after human verification; use is at the operator's discretion and requires further validation.

**Can I redistribute SROIE/CORD?** Only in accordance with their source-specific rights, not under this project's MIT license.

**What makes a contribution acceptable?** Correct module-level implementation, reproducible tests, exact measured claims, updated Indonesian and English docs, a meaningful commit and no sensitive data.

## License and citations

Source code: **MIT** (`../../LICENSE`). Third-party rights remain separate. Primary attribution targets: [SROIE ICDAR 2019](https://rrc.cvc.uab.es/?ch=13), [CORD v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2), [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Every shared chart and dataset-derived claim must identify its dataset and exact experimental protocol.
