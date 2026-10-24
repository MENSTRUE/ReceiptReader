# ReceiptReader evaluation protocol and report audit

## The unit of evaluation

A sample is one identified receipt image, matched to an independently verified ground-truth record. Four canonical field names: `company`, `date`, `address`, `total`. Before scoring, document case-folding/whitespace treatment, ISO date conversion, and monetary separator/currency rules. Keep both raw OCR and normalized candidate when allowed by source rights.

## Metrics and required labels

- `company_exact`, `date_exact`, `address_exact`, `total_exact`: fraction of samples with field exactly equal to gold after frozen normalization.
- `macro_exact`: arithmetic mean of four field exact-match rates, not a pixel OCR accuracy rate.
- `all_four_exact`: fraction of receipts for which all four fields match simultaneously.
- `address_token_f1`: distinct token-level metric; **not** equivalent to exact address match.
- Record N, failed requests, source, split, previous test inspection status, and image-vs-annotated-text protocol for each report.

## Committed v10 evidence

- `split_audit.json`: SROIE train 626, internal train 501/val 125; published test 361, 8 overlap excluded from 353 repeatedly inspected hash-clean images. CORD official training 800.
- `v10_repeated_pixel_metrics.json`: repeated-image evaluation on N=80; baseline and v10 are identical on all recorded field metrics. Company 0.525; date 0.75; address 0.3625; total 0.55; macro 0.546875; all-four 0.05.
- `total_comparison_validation.json`: SROIE validation total exact 0.808 vs 0.824 with CORD augmentation. This is a **different scope**.
- `v10_summary.json`: CORD validation total exact 0.95; cannot imply four-field app accuracy.

## Current app baseline and evidence gate

No matched independent app benchmark is committed. The local test screenshot demonstrates one example (company/date/address/total) and is a smoke test only; do not report 4/4 as 100% test-set accuracy. To publish an app metric, run a frozen licensed image cohort with independently reviewed labels, compare via this exact contract, store predictions and a dated aggregate report, and include failure breakdowns with redactions.

## Data privacy and release restrictions

Check licensing before publishing any images or OCR text. Do not commit raw transaction photos, original third-party annotations or user-identifiable data. Keep review exports local under `exports/` (ignored by Git). If only aggregate metrics may be published, preserve a private, authorized audit trail without putting data in the repository.
