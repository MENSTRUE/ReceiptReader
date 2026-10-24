# ReceiptReader — Day 17/100

A **review-first receipt OCR prototype** for merchant/company, date, address and total. The current runnable baseline uses Tesseract OCR plus transparent extraction heuristics; it **does not** load the research v10 model. This distinction is mandatory for honest demos.

## Start (Windows / PowerShell)

1. Install Python 3.11 and [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki); ensure `tesseract --version` works (otherwise set the path explicitly in `src/receiptreader/ocr.py`).
2. `py -3.11 -m venv .venv`
3. `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
4. `.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py`
5. Tests: `.\.venv\Scripts\python.exe -m pytest -q`

Workflow: upload receipt image → preprocess → OCR → candidate fields → **manual correction** → verify → export JSON/CSV. `address` defaults blank rather than suggesting an unreliable fabricated address. `total` is extracted only from candidate total lines and must be checked for OCR/currency errors.

## Before / Now / Next

- **Before:** Kaggle research v10 tested SROIE receipt OCR/KIE, including pixel evaluations. Results are research-only and evaluation protocols differ across reported subsets.
- **Now:** Runnable baseline inference/app and a repository contract. No v10 models have been copied or audited. No accuracy claim is made for this scaffold.
- **Next:** Inspect the **actual v10 ZIP, notebook and saved artifacts**, identify whether inference depends on Tesseract/handcrafted rules/learned models, rebuild exact preprocessing, add fixture parity tests, then integrate verified components.

## Evaluation limits

SROIE is Malaysian receipt data; CORD v2 includes Indonesian receipts but provides different labels. Domain transfer is not guaranteed. SROIE address extraction was especially weak in earlier experiments. A user correction workflow is essential. Do not compare repeat-used annotated-text testing with image-to-fields pixel testing as if they were equivalent, or claim production reliability.

## Data provenance

- SROIE receipts: see official ICDAR 2019 SROIE task and source licensing before redistribution.
- CORD v2: https://huggingface.co/datasets/naver-clova-ix/cord-v2 — different label schema, not automatically address/company/date ground truth.
- Do not commit third-party raw receipts, credentials or personal receipt data.

[Dokumentasi Indonesia](docs/id/README.md) · [English documentation](docs/en/README.md) · [Agent rules](AGENTS.md)

Source code is MIT as described in the repository LICENSE; **dataset licenses are separate**.
