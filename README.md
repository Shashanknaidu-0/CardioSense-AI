# CardioSense AI — Explainable Cardiovascular Disease Risk Prediction

## What changed in this pass

The existing prediction engine (`app/predictor.py`) was **not modified** —
same models, same weights, same thresholds, same feature engineering.

- **Fixed a crash-on-launch bug**: `st.set_page_config()` was not the
  first Streamlit command in `app.py` — `load_predictor()` (wrapped
  in `@st.cache_resource`, which itself issues Streamlit commands)
  ran before it. This raised
  `StreamlitSetPageConfigMustBeFirstCommandError` on every launch.
  Fixed by moving `set_page_config()` to the very top of the file.
  (This bug pre-dated this pass — it was already present in the
  original `app.py` order, just hadn't been triggered on a run yet.)
- **Fixed a version-pinning issue**: `preprocessing/imputer.pkl` and
  `preprocessing/scaler.pkl` were pickled with **scikit-learn
  1.6.1**. `requirements.txt` previously allowed any `scikit-learn
  >= 1.4`, so `pip install` could silently leave a newer,
  incompatible scikit-learn in place, causing
  `AttributeError: 'SimpleImputer' object has no attribute
  '_fill_dtype'` at prediction time. `requirements.txt` now pins
  `scikit-learn==1.6.1` exactly. If you need a newer scikit-learn,
  you'll need to re-fit and re-save both `.pkl` files with that
  version.
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

## A cosmetic (harmless) console error you may still see

```
Examining the path of torch.classes raised:
...
RuntimeError: Tried to instantiate class '__path__._path' ...
```

This is a known Streamlit + PyTorch interaction: Streamlit's file
watcher tries to introspect `torch.classes.__path__` for hot-reload
purposes and torch's custom module loader doesn't support that
introspection. It's caught and logged by Streamlit, not a crash —
the app keeps running. If it bothers you, add this to
`.streamlit/config.toml`:

```toml
[server]
fileWatcherType = "none"
```

(This disables auto-reload-on-save, so only do this if that's an
acceptable trade-off for you.)

## Important — please re-test after this fix

This container still has no network access, so I can't install and
run streamlit/torch/lightgbm/xgboost/shap myself. The two bugs above
were found from your actual traceback and are now fixed and
syntax-checked, but please re-run to confirm:

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
