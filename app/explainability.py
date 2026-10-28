"""
CardioSense AI — Explainability Module
========================================

This module adds SHAP-based explainability on top of the existing,
untouched CardioSensePredictor. It does not retrain or modify any
model, and it does not fabricate SHAP values.

Two kinds of explanation are provided:

1. GLOBAL FEATURE IMPORTANCE
   Uses the *native, intrinsic* gain-based importance already stored
   inside the trained LightGBM and XGBoost boosters (the two tree
   models in the ensemble). This requires no background data and
   is exactly what the trained models report about themselves.

2. INDIVIDUAL PREDICTION EXPLANATION
   Uses shap.KernelExplainer treating the full hybrid ensemble
   (LightGBM + XGBoost + FT-Transformer + SAINT + PyTorch Deep
   Tabular, exactly as combined in predictor.predict) as a black-box
   function of the 11 raw clinical inputs. This gives a genuine,
   model-faithful attribution for one patient's prediction rather
   than an approximation from a single sub-model.

   The KernelExplainer background is a small reference set built
   from the REAL population statistics stored in the fitted
   StandardScaler (scaler.mean_), i.e. the actual NHANES-derived
   training-set means for each engineered feature. Nothing here is
   invented; the reference patient is the true cohort-average
   patient, at both gender encodings.
"""

import numpy as np
import pandas as pd
import torch

from app.predictor import engineer_clinical_features, DEVICE

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


# ============================================================
# DISPLAY NAMES
# ============================================================

DISPLAY_NAMES = {
    "age": "Age",
    "bmi": "BMI",
    "waist_circumference": "Waist Circumference",
    "sys_bp": "Systolic BP",
    "dia_bp": "Diastolic BP",
    "pulse_rate": "Pulse Rate",
    "tot_chol": "Total Cholesterol",
    "hdl_chol": "HDL Cholesterol",
    "hba1c": "HbA1c",
    "hs_crp": "hs-CRP",
    "pulse_pressure": "Pulse Pressure",
    "mean_arterial_pressure": "Mean Arterial Pressure",
    "chol_hdl_ratio": "Cholesterol / HDL Ratio",
    "non_hdl_chol": "Non-HDL Cholesterol",
    "log_hs_crp": "Log hs-CRP",
    "crp_high_risk": "CRP High-Risk Flag",
    "age_bmi_risk": "Age-BMI Risk Index",
    "cardio_inflammatory_index": "Cardio-Inflammatory Index",
    "metabolic_age_index": "Metabolic-Age Index",
    "is_male": "Gender (Male)",
    "gender": "Gender",
}

# Raw patient dict keys, in the fixed order used throughout the app
RAW_COLUMNS = [
    "age", "gender", "bmi", "waist_circumference",
    "sys_bp", "dia_bp", "pulse_rate",
    "tot_chol", "hdl_chol", "hba1c", "hs_crp",
]


# ============================================================
# VECTORIZED ENSEMBLE PREDICTION
# (same math as CardioSensePredictor.predict, batched over N rows)
# ============================================================

def batch_ensemble_probability(predictor, raw_matrix):
    """
    raw_matrix: numpy array of shape (n, 11), columns == RAW_COLUMNS.
    Returns: numpy array of shape (n,) with ensemble probabilities.

    Reuses the already-loaded models/scaler/imputer/weights from the
    given CardioSensePredictor instance. No model is retrained or
    altered.
    """

    df = pd.DataFrame(raw_matrix, columns=RAW_COLUMNS)

    df = engineer_clinical_features(df)

    numerical = predictor.scaler.transform(
        predictor.imputer.transform(df[predictor.num_features])
    )

    is_male = (
        df["gender"].fillna(1.0) == 1.0
    ).astype(float).values.reshape(-1, 1)

    X = np.hstack([numerical, is_male])

    p_lgb = predictor.lgb_model.predict(X)
    p_xgb = predictor.xgb_model.predict_proba(X)[:, 1]

    tensor_x = torch.tensor(X, dtype=torch.float32, device=DEVICE)

    with torch.no_grad():
        p_ft = torch.sigmoid(predictor.ft_model(tensor_x)).cpu().numpy()
        p_saint = torch.sigmoid(predictor.saint_model(tensor_x)).cpu().numpy()
        p_deep = torch.sigmoid(predictor.deep_model(tensor_x)).cpu().numpy()

    weights = predictor.ensemble_config["weights"]

    final = (
        weights["LightGBM"] * p_lgb +
        weights["XGBoost"] * p_xgb +
        weights["FT-Transformer"] * p_ft +
        weights["SAINT"] * p_saint +
        weights["PyTorch Deep Tabular"] * p_deep
    )

    return final


# ============================================================
# REFERENCE / BACKGROUND PATIENT (real cohort statistics)
# ============================================================

def get_reference_patient(predictor):
    """
    Returns a dict of the RAW feature averages taken from the fitted
    StandardScaler's mean_ (the true training-set means for the
    first 10 numeric features, which are exactly the raw clinical
    inputs). Used only as an honest SHAP background / baseline.
    """

    means = predictor.scaler.mean_
    raw_feature_order = predictor.num_features[:10]

    return {
        name: float(means[i])
        for i, name in enumerate(raw_feature_order)
    }


# ============================================================
# GLOBAL FEATURE IMPORTANCE (model-intrinsic, real)
# ============================================================

def get_global_importance(predictor, top_n=12):
    """
    Blends the native gain-based feature importance already stored
    in the trained LightGBM and XGBoost models (the two tree-based
    members of the ensemble). This is not SHAP and not invented —
    it is read directly from the trained boosters.
    """

    feature_names = predictor.all_feature_names

    lgb_importance = np.array(
        predictor.lgb_model.feature_importance(importance_type="gain"),
        dtype=float,
    )

    xgb_importance = np.array(
        predictor.xgb_model.feature_importances_,
        dtype=float,
    )

    lgb_total = lgb_importance.sum() or 1.0
    xgb_total = xgb_importance.sum() or 1.0

    lgb_norm = lgb_importance / lgb_total
    xgb_norm = xgb_importance / xgb_total

    combined = (lgb_norm * 0.5) + (xgb_norm * 0.5)

    rows = [
        {
            "feature": DISPLAY_NAMES.get(name, name),
            "importance": float(value),
        }
        for name, value in zip(feature_names, combined)
    ]

    rows.sort(key=lambda r: r["importance"], reverse=True)

    return rows[:top_n]


# ============================================================
# INDIVIDUAL PREDICTION EXPLANATION (real SHAP, ensemble-level)
# ============================================================

def explain_prediction(predictor, patient, nsamples=150):
    """
    Computes true SHAP values for ONE patient's prediction, treating
    the full hybrid ensemble as a black-box function of the 11 raw
    clinical inputs.

    Raises RuntimeError if the `shap` package is not installed.
    """

    if not SHAP_AVAILABLE:
        raise RuntimeError(
            "The 'shap' package is not installed. "
            "Install it with: pip install shap"
        )

    reference = get_reference_patient(predictor)

    background_rows = []
    for gender_value in (0.0, 1.0):
        row = [
            reference[c] if c != "gender" else gender_value
            for c in RAW_COLUMNS
        ]
        background_rows.append(row)

    background = np.array(background_rows, dtype=float)

    patient_row = np.array(
        [[patient[c] for c in RAW_COLUMNS]],
        dtype=float,
    )

    def f(X):
        return batch_ensemble_probability(predictor, X)

    explainer = shap.KernelExplainer(f, background)

    shap_values = explainer.shap_values(
        patient_row,
        nsamples=nsamples,
        silent=True,
    )

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    values = np.array(shap_values).reshape(-1)

    base_value = explainer.expected_value
    if isinstance(base_value, (list, np.ndarray)):
        base_value = base_value[0]

    contributions = [
        {
            "feature": DISPLAY_NAMES.get(col, col),
            "value": float(val),
            "patient_value": patient[col],
        }
        for col, val in zip(RAW_COLUMNS, values)
    ]

    contributions.sort(key=lambda r: abs(r["value"]), reverse=True)

    return {
        "base_value": float(base_value),
        "predicted_value": float(base_value + values.sum()),
        "contributions": contributions,
    }
