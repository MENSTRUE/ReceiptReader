# ReceiptReader engineering contract (coding agents)

## Intent
Day 17 portfolio receipt OCR/KIE demo with honest evaluation. Do not turn this into a generic chatbot or fabricate model metrics.

## Known research context
Prior SROIE / CORD research v10 used different evaluation setups; reported address failures and text-vs-pixel protocol differences matter. No v10 binary has been verified in this repository yet. Until verified, `src/receiptreader/ocr.py` is explicitly a Tesseract baseline. Never label baseline predictions as v10 or trained ML.

## Engineering rules
1. Keep testable inference components in `src/receiptreader`; UI under `app`.
2. Never silently merge dataset annotations with different label meanings. Store split hashes and dedup logic when adding test data.
3. Report raw OCR, per-field exact match, fully-correct receipt rate and source/protocol/sample sizes; no invented accuracy or calibration.
4. User must be able to edit **all** fields before CSV/JSON export; do not log receipts.
5. Avoid adding placeholder files, untracked model names or dummy predictions.
6. Use `requirements.txt` with system Tesseract installation described separately; verify `pytest -q` and one-image Streamlit smoke.
7. Data sources and redistribution rights must appear in bilingual docs, with training/validation/test boundaries.
8. `pass/` is documentation for access procedures only. Never store passwords/tokens/API keys.
9. Add commit messages for meaningful changes. Never commit `exports/`, receipt uploads, local envs, or original datasets.
10. Source license ≠ model license ≠ dataset license; keep claims separate.

## Artifacts
`models/` actual binary + manifest only after audit; `reports/` measured JSON, plots and methodology; `assets/` screenshots derived from real app; `notebooks/` reproducible experiments; `exports/` ignored local results.

## Migration checklist for v10
Audit archive listing, open last notebook, enumerate imports and trained artifacts, run frozen test image through notebook, implement exact wrapper and compare field-by-field; update source contract before calling it integrated.
