# CardioSense AI — Explainable Cardiovascular Disease Risk Prediction

## What changed in this pass

The existing prediction engine (`app/predictor.py`) was **not modified** —
same models, same weights, same thresholds, same feature engineering.

- Fixed a bug in the Risk Calculator results section: it was reading
  `result["risk_probability"]`, `result["individual_predictions"]` and
  `result["threshold_decisions"]`, but `predictor.predict()` actually
  returns `probability`, `models` and `decisions`. This would raise a
  `KeyError` on every real prediction. Now fixed and rendered as a
  clean risk gauge, per-model cards, and threshold cards.
- Removed a leftover duplicate/stub HTML block that rendered after
  the real Risk Calculator page ("The actual CardioSense AI
  prediction interface will be connected here next.").
- Trimmed navigation to the 5 requested pages (removed **Dataset**
  and **About**; renamed **AI Model** → **AI Models**).
- Built out **AI Models**, **Explainability**, and **Methodology**,
  which were previously `st.info()` placeholders.
- Added `app/explainability.py` — a new module (predictor.py
  untouched) that adds:
  - **Global feature importance**: real gain-based importance read
    directly from the trained LightGBM/XGBoost boosters (no
    fabrication, no extra training).
  - **Individual prediction explanation**: real SHAP values via
    `shap.KernelExplainer`, treating the full 5-model ensemble as
    the function being explained, with a background reference
    patient built from the *actual* stored `StandardScaler.mean_`
    (real NHANES-derived cohort averages) — not invented data.
- Added `requirements.txt` and `.streamlit/config.toml` (hides the
  deploy/menu toolbar reliably, sets the light theme).

## Important — please test this yourself before presenting it

This container has **no network access**, so `streamlit`, `lightgbm`,
`xgboost`, `torch`, and `shap` could not be installed or run here.
Every file was written and syntax-checked (`python -m py_compile`),
and the code was written by carefully reading your real
`predictor.py`, `feature_config.json`, and `ensemble_config.json` —
but it has **not been executed end-to-end**. Please run it locally:

```bash
pip install -r requirements.txt
python test_prediction.py     # sanity-checks the predictor in isolation
streamlit run app.py
```

If `shap` isn't installed, the rest of the app still works — the
Explainability page's individual-prediction section will show a
friendly warning instead of crashing.

## Project structure

```
CardioSense-AI/
├── app.py                    # Main Streamlit app (navigation + all 5 pages)
├── requirements.txt
├── .streamlit/config.toml
├── app/
│   ├── __init__.py
│   ├── predictor.py          # UNCHANGED — your original prediction engine
│   └── explainability.py     # NEW — SHAP + native feature importance
├── models/                   # UNCHANGED model artifacts
│   ├── lightgbm_model.txt
│   ├── xgboost_model.json
│   ├── feature_config.json
│   ├── ensemble_config.json
│   ├── pytorch_config.json
│   └── pytorch/
│       ├── ft_transformer.pt
│       ├── saint.pt
│       └── deep_tabular.pt
├── preprocessing/             # UNCHANGED
│   ├── imputer.pkl
│   └── scaler.pkl
├── assets/
└── test_prediction.py         # UNCHANGED
```
