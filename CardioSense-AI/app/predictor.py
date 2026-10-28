import os
import json
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
import torch
import torch.nn as nn


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "models")
PREPROCESS_DIR = os.path.join(BASE_DIR, "preprocessing")


# ============================================================
# FEATURE ENGINEERING
# EXACTLY MATCHES THE COLAB NOTEBOOK
# ============================================================

def engineer_clinical_features(data):

    d = data.copy()

    # Hemodynamics
    d["pulse_pressure"] = d["sys_bp"] - d["dia_bp"]

    d["mean_arterial_pressure"] = (
        d["dia_bp"] +
        (d["sys_bp"] - d["dia_bp"]) / 3.0
    )

    # Lipid ratios
    d["chol_hdl_ratio"] = (
        d["tot_chol"] /
        (d["hdl_chol"] + 1e-5)
    )

    d["non_hdl_chol"] = (
        d["tot_chol"] -
        d["hdl_chol"]
    )

    # Inflammatory features
    crp_safe = np.maximum(
        d["hs_crp"].fillna(1.5),
        0
    )

    d["log_hs_crp"] = np.log1p(crp_safe)

    d["crp_high_risk"] = (
        d["hs_crp"] > 3.0
    ).astype(float)

    # Cardiometabolic interactions
    d["age_bmi_risk"] = (
        d["age"] / 10.0
    ) * (
        d["bmi"] / 10.0
    )

    d["cardio_inflammatory_index"] = (
        d["sys_bp"] / 120.0
    ) * (
        d["log_hs_crp"] + 1.0
    )

    d["metabolic_age_index"] = (
        d["hba1c"] / 5.7
    ) * (
        d["age"] / 50.0
    )

    return d


# ============================================================
# PYTORCH MODEL DEFINITIONS
# EXACTLY MATCH THE COLAB NOTEBOOK
# ============================================================

class FeatureTokenizer(nn.Module):

    def __init__(
        self,
        num_features,
        d_token=32
    ):
        super().__init__()

        self.num_features = num_features
        self.d_token = d_token

        self.weight = nn.Parameter(
            torch.empty(num_features, d_token)
        )

        self.bias = nn.Parameter(
            torch.empty(num_features, d_token)
        )

        self.cls_token = nn.Parameter(
            torch.empty(1, 1, d_token)
        )

        nn.init.kaiming_uniform_(
            self.weight,
            a=np.sqrt(5)
        )

        nn.init.kaiming_uniform_(
            self.bias,
            a=np.sqrt(5)
        )

        nn.init.normal_(
            self.cls_token,
            std=0.02
        )

    def forward(self, x):

        batch_size = x.shape[0]

        tokens = (
            x.unsqueeze(-1)
            * self.weight
            + self.bias
        )

        cls = self.cls_token.expand(
            batch_size,
            -1,
            -1
        )

        return torch.cat(
            [cls, tokens],
            dim=1
        )


class FTTransformerNet(nn.Module):

    def __init__(
        self,
        num_features,
        d_token=32,
        n_blocks=2,
        n_heads=4,
        d_ffn_factor=2.0,
        dropout=0.1
    ):

        super().__init__()

        self.tokenizer = FeatureTokenizer(
            num_features,
            d_token
        )

        dim_feedforward = int(
            d_token * d_ffn_factor
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_token,
            nhead=n_heads,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=n_blocks
        )

        self.norm = nn.LayerNorm(d_token)

        self.head = nn.Linear(
            d_token,
            1
        )

    def forward(self, x):

        tokens = self.tokenizer(x)

        x_trans = self.transformer(tokens)

        cls_out = self.norm(
            x_trans[:, 0, :]
        )

        return self.head(
            cls_out
        ).squeeze(-1)


class SelfAttentionBlock(nn.Module):

    def __init__(
        self,
        d_token,
        n_heads=4,
        dropout=0.1
    ):

        super().__init__()

        self.attn = nn.MultiheadAttention(
            embed_dim=d_token,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )

        self.norm1 = nn.LayerNorm(d_token)

        self.ffn = nn.Sequential(
            nn.Linear(
                d_token,
                d_token * 2
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                d_token * 2,
                d_token
            )
        )

        self.norm2 = nn.LayerNorm(d_token)

    def forward(self, x):

        attn_out, _ = self.attn(
            x,
            x,
            x
        )

        x = self.norm1(
            x + attn_out
        )

        ffn_out = self.ffn(x)

        return self.norm2(
            x + ffn_out
        )


class IntersampleAttentionBlock(nn.Module):

    def __init__(
        self,
        d_token,
        n_heads=4,
        dropout=0.1
    ):

        super().__init__()

        self.attn = nn.MultiheadAttention(
            embed_dim=d_token,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )

        self.norm1 = nn.LayerNorm(d_token)

        self.ffn = nn.Sequential(
            nn.Linear(
                d_token,
                d_token * 2
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                d_token * 2,
                d_token
            )
        )

        self.norm2 = nn.LayerNorm(d_token)

    def forward(self, x):

        x_trans = x.transpose(0, 1)

        attn_out, _ = self.attn(
            x_trans,
            x_trans,
            x_trans
        )

        x_trans = self.norm1(
            x_trans + attn_out
        )

        ffn_out = self.ffn(x_trans)

        x_trans = self.norm2(
            x_trans + ffn_out
        )

        return x_trans.transpose(0, 1)


class SAINTBlock(nn.Module):

    def __init__(
        self,
        d_token,
        n_heads=4,
        dropout=0.1
    ):

        super().__init__()

        self.self_attn = SelfAttentionBlock(
            d_token,
            n_heads,
            dropout
        )

        self.intersample_attn = IntersampleAttentionBlock(
            d_token,
            n_heads,
            dropout
        )

    def forward(self, x):

        return self.intersample_attn(
            self.self_attn(x)
        )


class SAINTNet(nn.Module):

    def __init__(
        self,
        num_features,
        d_token=32,
        n_blocks=2,
        n_heads=4,
        dropout=0.1
    ):

        super().__init__()

        self.tokenizer = FeatureTokenizer(
            num_features,
            d_token
        )

        self.blocks = nn.ModuleList([
            SAINTBlock(
                d_token=d_token,
                n_heads=n_heads,
                dropout=dropout
            )
            for _ in range(n_blocks)
        ])

        self.norm = nn.LayerNorm(d_token)

        self.head = nn.Linear(
            d_token,
            1
        )

    def forward(self, x):

        tokens = self.tokenizer(x)

        for block in self.blocks:

            tokens = block(tokens)

        cls_out = self.norm(
            tokens[:, 0, :]
        )

        return self.head(
            cls_out
        ).squeeze(-1)


class TabularResNet(nn.Module):

    def __init__(self, in_dim):

        super().__init__()

        self.in_block = nn.Sequential(
            nn.Linear(
                in_dim,
                64
            ),
            nn.BatchNorm1d(64),
            nn.SiLU(),
            nn.Dropout(0.2)
        )

        self.res_block = nn.Sequential(
            nn.Linear(
                64,
                64
            ),
            nn.BatchNorm1d(64),
            nn.SiLU(),
            nn.Dropout(0.2),
            nn.Linear(
                64,
                64
            ),
            nn.BatchNorm1d(64)
        )

        self.head = nn.Sequential(
            nn.Linear(64, 32),
            nn.SiLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1)
        )

        self.act = nn.SiLU()

    def forward(self, x):

        h0 = self.in_block(x)

        h_res = self.act(
            h0 + self.res_block(h0)
        )

        return self.head(
            h_res
        ).squeeze(1)


# ============================================================
# CARDIOSENSE PREDICTOR
# ============================================================

class CardioSensePredictor:

    def __init__(self):

        # ----------------------------------------------------
        # Load configuration
        # ----------------------------------------------------

        with open(
            os.path.join(
                MODEL_DIR,
                "feature_config.json"
            ),
            "r"
        ) as f:
            self.feature_config = json.load(f)

        with open(
            os.path.join(
                MODEL_DIR,
                "ensemble_config.json"
            ),
            "r"
        ) as f:
            self.ensemble_config = json.load(f)

        # ----------------------------------------------------
        # Feature names
        # ----------------------------------------------------

        self.num_features = (
            self.feature_config["num_features"]
        )

        self.all_feature_names = (
            self.feature_config["all_feature_names"]
        )

        self.input_dimension = (
            self.feature_config["input_dimension"]
        )

        # ----------------------------------------------------
        # Preprocessing
        # ----------------------------------------------------

        self.imputer = joblib.load(
            os.path.join(
                PREPROCESS_DIR,
                "imputer.pkl"
            )
        )

        self.scaler = joblib.load(
            os.path.join(
                PREPROCESS_DIR,
                "scaler.pkl"
            )
        )

        # ----------------------------------------------------
        # LightGBM
        # ----------------------------------------------------

        self.lgb_model = lgb.Booster(
            model_file=os.path.join(
                MODEL_DIR,
                "lightgbm_model.txt"
            )
        )

        # ----------------------------------------------------
        # XGBoost
        # ----------------------------------------------------

        self.xgb_model = xgb.XGBClassifier()

        self.xgb_model.load_model(
            os.path.join(
                MODEL_DIR,
                "xgboost_model.json"
            )
        )

        # ----------------------------------------------------
        # FT-Transformer
        # ----------------------------------------------------

        self.ft_model = FTTransformerNet(
            num_features=self.input_dimension,
            d_token=32,
            n_blocks=2,
            n_heads=4,
            d_ffn_factor=2.0,
            dropout=0.1
        ).to(DEVICE)

        self.ft_model.load_state_dict(
            torch.load(
                os.path.join(
                    MODEL_DIR,
                    "pytorch",
                    "ft_transformer.pt"
                ),
                map_location=DEVICE
            )
        )

        # ----------------------------------------------------
        # SAINT
        # ----------------------------------------------------

        self.saint_model = SAINTNet(
            num_features=self.input_dimension,
            d_token=32,
            n_blocks=2,
            n_heads=4,
            dropout=0.1
        ).to(DEVICE)

        self.saint_model.load_state_dict(
            torch.load(
                os.path.join(
                    MODEL_DIR,
                    "pytorch",
                    "saint.pt"
                ),
                map_location=DEVICE
            )
        )

        # ----------------------------------------------------
        # Deep Tabular
        # ----------------------------------------------------

        self.deep_model = TabularResNet(
            self.input_dimension
        ).to(DEVICE)

        self.deep_model.load_state_dict(
            torch.load(
                os.path.join(
                    MODEL_DIR,
                    "pytorch",
                    "deep_tabular.pt"
                ),
                map_location=DEVICE
            )
        )

        # ----------------------------------------------------
        # Evaluation mode
        # ----------------------------------------------------

        self.ft_model.eval()
        self.saint_model.eval()
        self.deep_model.eval()

    # ========================================================
    # PREPROCESS PATIENT
    # ========================================================

    def preprocess_patient(self, patient):

        df = pd.DataFrame([patient])

        # Exact notebook feature engineering
        df = engineer_clinical_features(df)

        # Numerical features
        numerical = self.scaler.transform(
            self.imputer.transform(
                df[self.num_features]
            )
        )

        # Exact notebook gender encoding:
        # Male = 1
        # Female = 0
        is_male = (
            df["gender"]
            .fillna(1.0)
            == 1.0
        ).astype(float).values.reshape(
            -1,
            1
        )

        X = np.hstack([
            numerical,
            is_male
        ])

        return X

    # ========================================================
    # PREDICT
    # ========================================================

    def predict(self, patient):

        X = self.preprocess_patient(
            patient
        )

        # ----------------------------------------------------
        # LightGBM
        # ----------------------------------------------------

        p_lgb = float(
            self.lgb_model.predict(X)[0]
        )

        # ----------------------------------------------------
        # XGBoost
        # ----------------------------------------------------

        p_xgb = float(
            self.xgb_model.predict_proba(
                X
            )[0, 1]
        )

        # ----------------------------------------------------
        # PyTorch models
        # ----------------------------------------------------

        tensor_x = torch.tensor(
            X,
            dtype=torch.float32,
            device=DEVICE
        )

        with torch.no_grad():

            p_ft = float(
                torch.sigmoid(
                    self.ft_model(tensor_x)
                ).cpu().numpy()[0]
            )

            p_saint = float(
                torch.sigmoid(
                    self.saint_model(tensor_x)
                ).cpu().numpy()[0]
            )

            p_deep = float(
                torch.sigmoid(
                    self.deep_model(tensor_x)
                ).cpu().numpy()[0]
            )

        # ----------------------------------------------------
        # Hybrid ensemble
        # ----------------------------------------------------

        weights = self.ensemble_config["weights"]

        final_probability = (
            weights["LightGBM"] * p_lgb +
            weights["XGBoost"] * p_xgb +
            weights["FT-Transformer"] * p_ft +
            weights["SAINT"] * p_saint +
            weights["PyTorch Deep Tabular"] * p_deep
        )

        # ----------------------------------------------------
        # Thresholds
        # ----------------------------------------------------

        thresholds = self.ensemble_config["thresholds"]

        result = {

            "probability": float(
                final_probability
            ),

            "risk_percent": float(
                final_probability * 100
            ),

            "models": {
                "LightGBM": p_lgb,
                "XGBoost": p_xgb,
                "FT-Transformer": p_ft,
                "SAINT": p_saint,
                "PyTorch Deep Tabular": p_deep
            },

            "thresholds": thresholds,

            "decisions": {

                "default": (
                    final_probability
                    >= thresholds["default"]
                ),

                "optimal_f1": (
                    final_probability
                    >= thresholds["optimal_f1"]
                ),

                "high_precision": (
                    final_probability
                    >= thresholds["high_precision"]
                ),

                "clinical_screening": (
                    final_probability
                    >= thresholds["clinical_screening"]
                )
            }
        }

        return result