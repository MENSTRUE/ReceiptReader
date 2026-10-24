# AGENTS.md — ReceiptReader Engineering & Scientific Source of Truth

> This is a **project contract for humans and coding agents**. Do not override it with assumptions from a screenshot, a notebook title, or a README claim. Read repository code, real artifacts and tests first. Date of contract: 2026-10-24.

## Project identity / decision hierarchy

- Repository: `MENSTRUE/ReceiptReader`; Day 17/100 portfolio project.
- Purpose: assist a human in reading receipts and verifying `company`, `date`, `address`, and `total`.
- **Primary invariant:** running app = Tesseract (PSM 6) + heuristic extractor + human confirmation. Research v10 outputs exist in `reports/` and `notebooks/`, but v10 **is not integrated** into live inference.
- If docs, notebooks, code and test evidence disagree, **working code + executed reproducible reports + tests** outrank descriptions; mark discrepancies and investigate rather than silently choosing the prettiest result.
- Never call smoke-test success or repeated test evaluation “production accuracy.”

## Before → Now → Next

1. **Before:** SROIE/CORD receipt OCR/KIE experimental work through research v10 with protocol differences, previously inspected SROIE images and weak address extraction.
2. **Now:** local review-first Streamlit app reads one sample receipt via Tesseract; user screenshot shows four correct fields on that sample. Remote GitHub might lag local code. There is no validated v10 app integration or held-out app benchmark.
3. **Next:** audit actual research artifacts, implement parity harness, add independent gold labels, evaluate field-level errors, assess privacy and release gating.

## Architecture / ownership of code

| Path | Responsibility | Do not do |
|---|---|---|
| `app/streamlit_app.py` | UI upload, preview, human verification, export | Fake accuracy banners, automatic trusted export, persistent raw receipt logging |
| `src/receiptreader/preprocessing.py` | EXIF correction and image preparation | Unrecorded or inconsistent preprocessing changes |
| `src/receiptreader/ocr.py` | Tesseract executable/config, PSM, language handling | Pretend `pytesseract` installs executable; silently fall back to invented text |
| `src/receiptreader/extraction.py` | Transparent and testable date/address/merchant/amount candidates | Guess missing values as certain; choose paid/change as total without evidence |
| `src/receiptreader/inference.py` | Model-neutral orchestration and output contract | Claim v10 use until actual parity verified |
| `src/receiptreader/schemas.py` | Typed four-field output contract | Break CSV/JSON field names without schema migration |
| `tests/` | Unit, regression, fixture, privacy, and parity tests | Adjust expected values only to inflate pass rates |
| `reports/` | Reproducible metrics and dataset audit | Mix per-protocol test numbers or fabricate missing rows |
| `notebooks/` | Reproducible experimental research | Publish execution without source/audit/config labels |
| `models/` | Verified inference assets, config, hashes | Empty fake .pt/.joblib/.safetensors files |
| `assets/plots/` | Authentic report plots | Generate illustrated charts that appear to be real metrics |
| `assets/screenshots/` | Real, sanitized screenshots | Synthetic screenshot evidence presented as actual UI |
| `exports/` | Local user-verified outputs, excluded from Git | Check in personal receipts or identifiers |
| `pass/` | Access/setup instructions only | Passwords, tokens, API keys, `.env`, Kaggle credentials |

## Source and dataset integrity

- SROIE ICDAR 2019: Malaysian receipts, target four fields. Repo `reports/split_audit.json`: 626 train; internal 501 train + 125 val; 361 published test; 8 duplicate-image hash overlaps excluded from 353 repeated hash-clean test. Ensure the split and dedup policy remains traceable.
- CORD v2: 800 official training items according to repo split audit, different annotation schema. In research, supports **total only** for four-field target; does not provide equivalent company/date/address gold fields.
- Preserve dataset versions, URLs, access/licensing, provenance, image/content hashes, normalized field definitions, label quality, image preprocessing and evaluation protocol. Read `reports/` first, not the v10 label on a filename.
- Do not publish proprietary or personally identifiable receipts. Delete or redact names, phone/address/order IDs as appropriate; obtain license/consent. MIT source code grant does not transfer third-party data rights.
- **For every metric:** report source, subset, exact N, dataset version, evaluation image/text protocol, metric definition, contamination/reuse, selection criterion, failure count, and confidence interval only when actually calculated.

## Numbers allowed in public claims

Use numbers only with scope and direct file evidence:

- `reports/v10_summary.json` and `reports/v10_repeated_pixel_metrics.json`: **80 repeated SROIE image/pixel** samples, company exact **52.50%**, date **75.00%**, address **36.25%**, total **55.00%**, macro **54.6875%**, all-four **5.00%**. Same numbers for `baseline` and `v10` in this file: **do not claim improvement on repeated pixel evaluation**.
- `reports/total_comparison_validation.json`: SROIE validation total exact **0.808** (`sroie_only`) and **0.824** (`cord_augmented`); research selection evidence, **not external app accuracy**.
- `reports/v10_summary.json`: CORD validation total exact **0.95** under distinct scope; **never use as overall four-field exact match**.
- Other report CSVs may represent annotated text vs pixel OCR; don't compare without matched samples/protocol.
- One locally checked illustrative Indonesian receipt: `TOKO MAJU JAYA`, `2025-04-12`, address `Jl. Melati No. 123…`, total `241980`. This is **one smoke**, not a validation cohort, and remote screenshot asset has not been verified.

## Application invariants & security

1. Never execute arbitrary shell/HTML commands from OCR text or user-supplied image metadata. Treat receipt content as untrusted.
2. Reject unreadable/corrupt images gracefully; limit file size and pixels; avoid decompression bombs.
3. Do not persist receipt images/raw OCR by default. Never print personal data into shared logs or telemetry.
4. Always preserve editable four fields, explicit review checkbox, and a confirm action for exports. Verification belongs to the user, not to inferred model confidence.
5. Keep amount **string** unless a documented currency/decimal parsing contract is introduced; avoid unsafe locale assumptions (`241.980` vs `241,980` vs `241.98`).
6. Empty candidate is safer than invented content when OCR evidence is missing/ambiguous. Expose raw OCR and review hints.
7. Give each upload a robust content hash, not just filename, when maintaining Streamlit session state. Clear prior confirmation on OCR reruns, changes or different file bytes. This is a recommended fix: verify code before claiming it is already implemented.
8. Support unknown/abstain/manual review; do not force an unsupported value.
9. In deployment use TLS, access control, retention policy, bounded jobs, diagnostics without PII, and dependency/security updates.

## Test and evaluation rules

### Tests required for each affected module

- Unit: dates (`12 Apr 2025`, ISO, invalid calendar), street-prefix OCR noise, multi-line address with postal code, merchant header, explicit total vs subtotal vs `Jumlah Bayar`, malformed/no amount, empty OCR.
- Regression: sample `TOKO MAJU JAYA` four expected values, with **sanitized/created data only**.
- Integration: Tesseract executable present; image preprocessing, OCR output and candidate fields consistent; app upload/review/edit/confirm/export path.
- Session-state: switching between two files with **same filename** must not reuse fields/confirmation.
- Scientific: frozen-image outputs from reproducible Kaggle v10 versus matching implementation, exact trace of config and dependencies.
- Deployment: fresh Python 3.11 environment and system OCR availability. CI without Tesseract may skip integration explicitly, not misreport passing OCR.

### Commands (Windows)

```powershell
cd "D:\porto\100 day\day 17\ReceiptReader"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

**Known repo mismatch:** `tests/test_extraction.py` on GitHub currently asserts legacy date `12/10/2026` while more recent local extractor behavior normalizes ISO `2026-10-12`. Make tests match the **intended documented contract** and add multiple cases; never claim current tests passed after unverified edits. Remote `src/receiptreader/ocr.py` also appears older than local Windows Tesseract auto-detection snippet.

## Research v10 integration gate (mandatory)

1. List exact notebook and release ZIP contents; locate saved weights/configs, model algorithm, OCR engine, PSM, decoder, threshold, normalization and input resolution.
2. Verify SHA-256, provenance/permissions, Python and package versions. Check whether “model” is a learned checkpoint, Tesseract/heuristic selection or both.
3. Extract frozen fixture set whose labels, prior inspection status and licensed publication rights are known.
4. Execute v10 notebook on exact image bytes; save **per-field raw and normalized outputs** with preprocessing trace.
5. Implement `src/receiptreader/` adapter without changing algorithm silently. Run equivalence against v10 output; document tolerated differences (if any).
6. Compare baseline vs v10 on same split and image protocol; add repeatability tests and precise metric labels.
7. Only after successful parity update app caption and docs to say v10 is integrated. If no transferable asset exists, keep baseline truthful and describe v10 as experiment.

## Development workflow / prompts

- Work **incrementally**: first terminal-built directory structure, user confirms; then deliver complete file code in its correct path; run tests/debug; supply meaningful git commit message; do not dump a ZIP of scaffolded code unless explicitly requested. For documentation packages requested by user, supply exact Markdown outputs without inventing missing program artifacts.
- Each change should include paths, purpose, full code or complete replacement, exact PowerShell commands, tests and expected vs observed distinction, migration notes, updated README/AGENTS if contract changes.
- Provide bilingual updates to `docs/id/README.md` and `docs/en/README.md` for claim-affecting code changes. No empty placeholder docs.
- Before merging, compare remote tree with local `git status` and `git diff`; source of truth is the code actually pushed, not an unsaved editor tab.
- Avoid committing datasets, generated exports, secrets, receipt uploads, unverified model binaries, notebook checkpoints or huge third-party ZIPs.

## Versioning, releases and legal

- Source LICENSE: MIT. Dataset and model weights may impose independent terms. Any demo screenshots require own imagery or rights and removal of sensitive details.
- A public release requires versioned config, requirements lock/constraints, model provenance, environment test, raw OCR failure handling, data usage terms, known limitations, human review and transparent test coverage.
- Suggested evidence manifest fields: `artifact`, `source`, `created_utc`, `commit_sha`, `dataset_version`, `protocol`, `n`, `metric_name`, `metric_value`, `sha256`, `rights`, `status`.

## Absolute prohibitions

No fabricated metrics, fake checkpoints, faked real screenshots, test-set-driven tuning masquerading as independent evaluation, assumption that synthetic image is held-out real receipt, automatic exporting unverified totals, personal-data logging, invented access tokens, or model replacement with undisclosed rule-based hardcoding. If data are missing, say **unavailable** and specify what evidence would establish the fact.
