import streamlit as st
from app.predictor import CardioSensePredictor
from app import explainability


@st.cache_resource
def load_predictor():
    return CardioSensePredictor()


try:
    predictor = load_predictor()
    predictor_load_error = None
except Exception as e:
    predictor = None
    predictor_load_error = str(e)
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CardioSense AI",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

    /* --------------------------------------------------------
       STREAMLIT UI
    -------------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        display: none;
    }


    /* --------------------------------------------------------
       APPLICATION BACKGROUND
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(219, 234, 254, 0.70),
                transparent 30%
            ),
            radial-gradient(
                circle at 95% 5%,
                rgba(224, 231, 255, 0.65),
                transparent 30%
            ),
            #f8fafc;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }


    /* --------------------------------------------------------
       HEADER
    -------------------------------------------------------- */

    .header-shell {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid #e2e8f0;
        border-radius: 18px;

        padding: 14px 20px;

        box-shadow:
            0 8px 30px rgba(15, 23, 42, 0.05);
    }

    .brand-title {
        color: #0f172a;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.6px;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }


    /* --------------------------------------------------------
       NAVIGATION
    -------------------------------------------------------- */

    div[data-testid="stPills"] {
        justify-content: flex-end;
    }

    div[data-testid="stPills"] button {
        border-radius: 11px !important;
        border: 1px solid transparent !important;

        background: transparent !important;

        color: #334155 !important;

        font-weight: 650 !important;

        padding: 8px 12px !important;

        transition: all 0.2s ease !important;
    }

    div[data-testid="stPills"] button:hover {
        background: #eaf2ff !important;
        border-color: #dbeafe !important;
        color: #1d4ed8 !important;
    }

    div[data-testid="stPills"] button[aria-checked="true"] {
        background: #e8f0ff !important;
        border-color: #bfdbfe !important;
        color: #1d4ed8 !important;
        font-weight: 750 !important;
    }


    /* --------------------------------------------------------
       HERO
    -------------------------------------------------------- */

    .hero-box {
        background:
            radial-gradient(
                circle at 86% 18%,
                rgba(96, 165, 250, 0.28),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #0b1220 0%,
                #111c3d 48%,
                #1d4ed8 100%
            );

        border-radius: 28px;

        padding: 68px 72px;

        margin-top: 30px;
        margin-bottom: 28px;

        min-height: 355px;

        display: flex;
        flex-direction: column;
        justify-content: center;

        box-shadow:
            0 25px 60px rgba(15, 23, 42, 0.16);
    }

    .hero-label {
        color: #93c5fd;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 20px;
    }

    .hero-title {
        color: white;
        font-size: 52px;
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: -1.8px;
        margin-bottom: 22px;
    }

    .hero-highlight {
        color: #60a5fa;
    }

    .hero-description {
        color: #cbd5e1;
        font-size: 17px;
        line-height: 1.7;
        max-width: 760px;
    }


    /* --------------------------------------------------------
       ACTION CARDS
    -------------------------------------------------------- */

    .action-heading {
        color: #0f172a;
        font-size: 17px;
        font-weight: 750;
        margin: 22px 0 15px 2px;
    }

    .action-card {
        background: rgba(255, 255, 255, 0.92);

        border: 1px solid #e2e8f0;

        border-radius: 18px;

        padding: 25px;

        min-height: 180px;

        box-shadow:
            0 6px 22px rgba(15, 23, 42, 0.045);
    }

    .action-icon {
        font-size: 28px;
        margin-bottom: 14px;
    }

    .action-title {
        color: #0f172a;
        font-size: 19px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .action-text {
        color: #64748b;
        font-size: 13px;
        line-height: 1.6;
    }

    .action-arrow {
        color: #2563eb;
        font-size: 13px;
        font-weight: 700;
        margin-top: 15px;
    }


    /* --------------------------------------------------------
       SECTION TITLES
    -------------------------------------------------------- */

    .section-title {
        color: #0f172a;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;

        margin-top: 45px;
        margin-bottom: 7px;
    }

    .section-description {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 24px;
    }


    /* --------------------------------------------------------
       STAT CARDS
    -------------------------------------------------------- */

    .stat-card {
        background: rgba(255, 255, 255, 0.94);

        border: 1px solid #e2e8f0;

        border-radius: 18px;

        padding: 25px 20px;

        min-height: 135px;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .stat-number {
        color: #1d4ed8;
        font-size: 30px;
        font-weight: 800;
    }

    .stat-label {
        color: #64748b;
        font-size: 13px;
        line-height: 1.4;
        margin-top: 6px;
    }


    /* --------------------------------------------------------
       FEATURE CARDS
    -------------------------------------------------------- */

    .feature-card {
        background: rgba(255, 255, 255, 0.94);

        border: 1px solid #e2e8f0;

        border-radius: 18px;

        padding: 28px;

        min-height: 205px;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .feature-icon {
        font-size: 28px;
        margin-bottom: 15px;
    }

    .feature-title {
        color: #0f172a;
        font-size: 19px;
        font-weight: 750;
        margin-bottom: 9px;
    }

    .feature-description {
        color: #64748b;
        font-size: 14px;
        line-height: 1.65;
    }


    /* --------------------------------------------------------
       PIPELINE
    -------------------------------------------------------- */

    .pipeline-card {
        background: rgba(255, 255, 255, 0.94);

        border: 1px solid #e2e8f0;

        border-radius: 20px;

        padding: 34px 25px;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .pipeline-number {
        background: #e8f0ff;

        color: #1d4ed8;

        width: 44px;
        height: 44px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        font-weight: 800;

        margin: auto;
    }

    .pipeline-name {
        text-align: center;

        color: #334155;

        font-size: 13px;

        font-weight: 700;

        margin-top: 12px;
    }


    /* --------------------------------------------------------
       PAGE HEADER
    -------------------------------------------------------- */

    .page-header {
        background: white;

        border: 1px solid #e2e8f0;

        border-radius: 20px;

        padding: 35px;

        margin-top: 30px;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .page-header-title {
        color: #0f172a;

        font-size: 34px;

        font-weight: 800;
    }

    .page-header-text {
        color: #64748b;

        font-size: 15px;

        line-height: 1.6;

        margin-top: 8px;
    }


    /* --------------------------------------------------------
       INFO BOX
    -------------------------------------------------------- */

    .info-box {
        background: #eff6ff;

        border: 1px solid #bfdbfe;

        border-radius: 16px;

        padding: 20px 24px;

        color: #1e3a8a;

        line-height: 1.65;
    }


    /* --------------------------------------------------------
       DISCLAIMER
    -------------------------------------------------------- */

    .disclaimer {
        background: #fff7ed;

        border: 1px solid #fed7aa;

        border-radius: 16px;

        padding: 20px 24px;

        color: #7c2d12;

        line-height: 1.6;

        margin-top: 35px;
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer-text {
        text-align: center;

        color: #94a3b8;

        font-size: 13px;

        line-height: 1.7;

        padding: 18px;
    }
/* ========================================================
   RISK CALCULATOR - PROFESSIONAL UI
======================================================== */

/* Section spacing */
[data-testid="stVerticalBlock"] {
    color: #0f172a;
}


/* --------------------------------------------------------
   INPUT LABELS
-------------------------------------------------------- */

[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    color: #334155 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}

[data-testid="stNumberInput"] label p,
[data-testid="stSelectbox"] label p {
    color: #334155 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}


/* --------------------------------------------------------
   NUMBER INPUT
-------------------------------------------------------- */

[data-testid="stNumberInput"] input {
    background: #ffffff !important;

    color: #0f172a !important;

    border: 1px solid #dbe3ef !important;

    border-radius: 12px !important;

    min-height: 44px !important;

    font-size: 14px !important;

    font-weight: 600 !important;
}

[data-testid="stNumberInput"] input:focus {
    border-color: #60a5fa !important;

    box-shadow:
        0 0 0 3px rgba(59, 130, 246, 0.12) !important;
}


/* Number input +/- buttons */

[data-testid="stNumberInput"] button {
    color: #475569 !important;

    background: transparent !important;

    border: none !important;
}

[data-testid="stNumberInput"] button:hover {
    color: #2563eb !important;

    background: #eff6ff !important;
}


/* --------------------------------------------------------
   SELECT BOX
-------------------------------------------------------- */

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #ffffff !important;

    border: 1px solid #dbe3ef !important;

    border-radius: 12px !important;

    min-height: 44px !important;

    color: #0f172a !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: #0f172a !important;

    font-weight: 600 !important;
}


/* --------------------------------------------------------
   INPUT HELP TEXT
-------------------------------------------------------- */

[data-testid="InputInstructions"] {
    color: #64748b !important;
}


/* --------------------------------------------------------
   METRIC / ASSESSMENT SUMMARY
-------------------------------------------------------- */

[data-testid="stMetric"] {
    background: #ffffff !important;

    border: 1px solid #e2e8f0 !important;

    border-radius: 16px !important;

    padding: 18px 20px !important;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.045) !important;
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;

    font-size: 12px !important;

    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748b !important;
}

[data-testid="stMetricValue"] {
    color: #0f172a !important;

    font-size: 24px !important;

    font-weight: 800 !important;
}


/* --------------------------------------------------------
   CALCULATE BUTTON
-------------------------------------------------------- */

div[data-testid="stButton"] > button {
    background: linear-gradient(
        135deg,
        #2563eb 0%,
        #1d4ed8 100%
    ) !important;

    color: #ffffff !important;

    border: none !important;

    border-radius: 14px !important;

    min-height: 52px !important;

    font-size: 15px !important;

    font-weight: 750 !important;

    box-shadow:
        0 8px 20px rgba(37, 99, 235, 0.20) !important;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease !important;
}

div[data-testid="stButton"] > button:hover {
    background: linear-gradient(
        135deg,
        #1d4ed8 0%,
        #1e40af 100%
    ) !important;

    transform: translateY(-2px) !important;

    box-shadow:
        0 12px 25px rgba(37, 99, 235, 0.25) !important;
}


/* --------------------------------------------------------
   CALCULATOR PAGE CARD
-------------------------------------------------------- */

.calculator-card {
    background: rgba(255, 255, 255, 0.88);

    border: 1px solid #e2e8f0;

    border-radius: 22px;

    padding: 28px;

    margin-top: 25px;

    box-shadow:
        0 10px 35px rgba(15, 23, 42, 0.05);
}


/* --------------------------------------------------------
   RESULT AREA
-------------------------------------------------------- */

.risk-result-card {
    background:
        linear-gradient(
            135deg,
            #eff6ff,
            #ffffff
        );

    border: 1px solid #bfdbfe;

    border-radius: 20px;

    padding: 28px;

    margin-top: 20px;

    box-shadow:
        0 10px 30px rgba(37, 99, 235, 0.08);
}

.risk-result-label {
    color: #64748b;

    font-size: 13px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 0.8px;
}

.risk-result-value {
    color: #1d4ed8;

    font-size: 48px;

    font-weight: 850;

    letter-spacing: -1.5px;

    margin-top: 5px;
}

.risk-status-tag {
    font-size: 14px;
    font-weight: 700;
    margin-top: 4px;
}

.risk-gauge-track {
    width: 100%;
    height: 12px;
    background: #e2e8f0;
    border-radius: 999px;
    margin-top: 22px;
    overflow: hidden;
}

.risk-gauge-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}

.risk-gauge-scale {
    display: flex;
    justify-content: space-between;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    margin-top: 6px;
}


/* --------------------------------------------------------
   MODEL PREDICTION CARDS
-------------------------------------------------------- */

.model-pred-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
    min-height: 110px;
}

.model-pred-name {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
}

.model-pred-value {
    color: #0f172a;
    font-size: 22px;
    font-weight: 800;
}

.model-pred-weight {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 6px;
}


/* --------------------------------------------------------
   THRESHOLD CARDS
-------------------------------------------------------- */

.threshold-card {
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    min-height: 100px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
}

.threshold-card.positive {
    background: #fef2f2;
    border-color: #fecaca;
}

.threshold-card.negative {
    background: #f0fdf4;
    border-color: #bbf7d0;
}

.threshold-name {
    color: #334155;
    font-size: 13px;
    font-weight: 750;
}

.threshold-cutoff {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 4px;
}

.threshold-status {
    font-size: 15px;
    font-weight: 800;
    margin-top: 8px;
}

.threshold-card.positive .threshold-status {
    color: #dc2626;
}

.threshold-card.negative .threshold-status {
    color: #059669;
}


/* --------------------------------------------------------
   AI MODELS PAGE
-------------------------------------------------------- */

.model-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 24px;
    min-height: 190px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
}

.model-card-icon {
    font-size: 26px;
    margin-bottom: 10px;
}

.model-card-title {
    color: #0f172a;
    font-size: 17px;
    font-weight: 750;
    margin-bottom: 6px;
}

.model-card-text {
    color: #64748b;
    font-size: 13px;
    line-height: 1.6;
}

.model-card-tag {
    display: inline-block;
    margin-top: 12px;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
}

.weight-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
}

.weight-name {
    width: 190px;
    flex-shrink: 0;
    color: #334155;
    font-size: 13px;
    font-weight: 700;
}

.weight-track {
    flex: 1;
    height: 14px;
    background: #eef2f7;
    border-radius: 999px;
    overflow: hidden;
}

.weight-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #2563eb, #60a5fa);
}

.weight-pct {
    width: 46px;
    text-align: right;
    color: #0f172a;
    font-size: 13px;
    font-weight: 800;
}


/* --------------------------------------------------------
   EXPLAINABILITY PAGE
-------------------------------------------------------- */

.importance-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}

.importance-name {
    width: 220px;
    flex-shrink: 0;
    color: #334155;
    font-size: 13px;
    font-weight: 650;
}

.importance-track {
    flex: 1;
    height: 12px;
    background: #eef2f7;
    border-radius: 999px;
    overflow: hidden;
}

.importance-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #1d4ed8, #93c5fd);
}

.shap-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
}

.shap-name {
    width: 210px;
    flex-shrink: 0;
    color: #334155;
    font-size: 13px;
    font-weight: 650;
}

.shap-name-value {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 500;
}

.shap-bar-area {
    flex: 1;
    height: 16px;
    background: #f1f5f9;
    border-radius: 8px;
    position: relative;
    display: flex;
    align-items: center;
}

.shap-bar-center {
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 1px;
    background: #cbd5e1;
}

.shap-bar-fill {
    height: 16px;
    position: absolute;
    border-radius: 6px;
}

.shap-bar-fill.increase {
    background: #f87171;
}

.shap-bar-fill.decrease {
    background: #34d399;
}

.shap-value-label {
    width: 70px;
    text-align: right;
    font-size: 12px;
    font-weight: 750;
}

.shap-value-label.increase {
    color: #dc2626;
}

.shap-value-label.decrease {
    color: #059669;
}

.legend-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 3px;
    margin-right: 6px;
}


/* --------------------------------------------------------
   METHODOLOGY PAGE
-------------------------------------------------------- */

.method-step {
    display: flex;
    gap: 18px;
    align-items: flex-start;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
}

.method-step-number {
    background: #e8f0ff;
    color: #1d4ed8;
    width: 38px;
    height: 38px;
    min-width: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
}

.method-step-title {
    color: #0f172a;
    font-size: 15.5px;
    font-weight: 750;
    margin-bottom: 4px;
}

.method-step-text {
    color: #64748b;
    font-size: 13.5px;
    line-height: 1.65;
}

.class-balance-track {
    width: 100%;
    height: 26px;
    border-radius: 999px;
    overflow: hidden;
    display: flex;
    margin-top: 14px;
    margin-bottom: 8px;
}

.class-balance-negative {
    background: #93c5fd;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1e3a8a;
    font-size: 11px;
    font-weight: 700;
}

.class-balance-positive {
    background: #1d4ed8;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 11px;
    font-weight: 700;
}


/* --------------------------------------------------------
   DIVIDERS
-------------------------------------------------------- */

hr {
    border-color: #e2e8f0 !important;
}


/* --------------------------------------------------------
   INFO / WARNING BOXES
-------------------------------------------------------- */

[data-testid="stAlert"] {
    border-radius: 14px !important;
}


/* --------------------------------------------------------
   MOBILE
-------------------------------------------------------- */

@media (max-width: 900px) {

    .hero-title {
        font-size: 38px;
    }

    .hero-box {
        padding: 45px 35px;
    }

    .page-header-title {
        font-size: 28px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [2.0, 6.0],
    vertical_alignment="center",
)


with header_left:

    st.html(
        """
        <div class="header-shell">

            <div class="brand-title">
                ❤️ CardioSense AI
            </div>

            <div class="brand-subtitle">
                Explainable cardiovascular risk intelligence
            </div>

        </div>
        """
    )


with header_right:

    navigation = st.pills(
        "Navigation",
        [
            "🏠 Home",
            "🩺 Risk Calculator",
            "🧠 AI Models",
            "🔬 Explainability",
            "⚙️ Methodology",
        ],
        selection_mode="single",
        default="🏠 Home",
        label_visibility="collapsed",
    )


# ============================================================
# MODEL LOAD GUARD
# ============================================================

if predictor_load_error is not None:

    st.error(
        "⚠️ CardioSense AI could not load its prediction engine. "
        "Please verify that the model, preprocessing and "
        "configuration files are present in this deployment."
    )

    with st.expander("Technical details (for developers)"):
        st.code(predictor_load_error)

    st.stop()


# ============================================================
# HOME PAGE
# ============================================================

if navigation == "🏠 Home":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.html(
        """
        <div class="hero-box">

            <div class="hero-label">
                AI-POWERED &nbsp; • &nbsp; EXPLAINABLE &nbsp; • &nbsp; CLINICAL AI
            </div>

            <div class="hero-title">
                Understand Cardiovascular Risk
                <br>
                with <span class="hero-highlight">Explainable AI</span>
            </div>

            <div class="hero-description">
                CardioSense AI combines clinical measurements,
                metabolic biomarkers and advanced machine-learning
                models to estimate cardiovascular disease risk
                and provide interpretable insights into the prediction.
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # ACTION CARDS
    # --------------------------------------------------------

    st.html(
        """
        <div class="action-heading">
            Explore CardioSense AI
        </div>
        """
    )


    a1, a2, a3 = st.columns(3)


    with a1:

        st.html(
            """
            <div class="action-card">

                <div class="action-icon">
                    🩺
                </div>

                <div class="action-title">
                    Risk Assessment
                </div>

                <div class="action-text">
                    Enter clinical measurements and biomarkers
                    to estimate cardiovascular disease risk.
                </div>

                <div class="action-arrow">
                    Start assessment →
                </div>

            </div>
            """
        )


    with a2:

        st.html(
            """
            <div class="action-card">

                <div class="action-icon">
                    🧠
                </div>

                <div class="action-title">
                    AI Models
                </div>

                <div class="action-text">
                    Explore the machine-learning and deep-learning
                    models powering CardioSense AI.
                </div>

                <div class="action-arrow">
                    Explore models →
                </div>

            </div>
            """
        )


    with a3:

        st.html(
            """
            <div class="action-card">

                <div class="action-icon">
                    🔬
                </div>

                <div class="action-title">
                    Explainability
                </div>

                <div class="action-text">
                    Understand which clinical features influence
                    the model's predictions.
                </div>

                <div class="action-arrow">
                    Explore explanations →
                </div>

            </div>
            """
        )


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            CardioSense AI at a Glance
        </div>

        <div class="section-description">
            The research foundation behind the prediction system.
        </div>
        """
    )


    c1, c2, c3, c4 = st.columns(4)


    stats = [
        (
            c1,
            "11,286",
            "Adult participants used for modeling",
        ),
        (
            c2,
            "20",
            "Clinical & engineered features",
        ),
        (
            c3,
            "5",
            "ML / deep-learning models",
        ),
        (
            c4,
            "2015–2018",
            "NHANES data cycles",
        ),
    ]


    for column, number, label in stats:

        with column:

            st.html(
                f"""
                <div class="stat-card">

                    <div class="stat-number">
                        {number}
                    </div>

                    <div class="stat-label">
                        {label}
                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Built for Transparent AI
        </div>

        <div class="section-description">
            CardioSense AI focuses on prediction,
            advanced modeling and interpretability.
        </div>
        """
    )


    f1, f2, f3 = st.columns(3)


    features = [
        (
            f1,
            "🤖",
            "Hybrid AI",
            "Five complementary machine-learning and deep-learning "
            "models are combined through probability-based ensemble prediction.",
        ),
        (
            f2,
            "🔬",
            "Explainable Predictions",
            "SHAP-based analysis helps identify which clinical and "
            "biomarker features contribute to an individual prediction.",
        ),
        (
            f3,
            "🧬",
            "Clinical Features",
            "The system uses demographic information, vital signs, "
            "metabolic biomarkers and inflammatory measurements.",
        ),
    ]


    for column, icon, title, description in features:

        with column:

            st.html(
                f"""
                <div class="feature-card">

                    <div class="feature-icon">
                        {icon}
                    </div>

                    <div class="feature-title">
                        {title}
                    </div>

                    <div class="feature-description">
                        {description}
                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            How CardioSense AI Works
        </div>

        <div class="section-description">
            From patient information to an explainable
            cardiovascular risk estimate.
        </div>
        """
    )


    st.html('<div class="pipeline-card">')

    p1, p2, p3, p4, p5 = st.columns(5)


    pipeline = [
        (p1, "1", "Patient Data"),
        (p2, "2", "Feature Engineering"),
        (p3, "3", "ML / DL Models"),
        (p4, "4", "Hybrid Ensemble"),
        (p5, "5", "Explainable Risk"),
    ]


    for column, number, name in pipeline:

        with column:

            st.html(
                f"""
                <div class="pipeline-number">
                    {number}
                </div>

                <div class="pipeline-name">
                    {name}
                </div>
                """
            )


    st.html("</div>")


    # --------------------------------------------------------
    # RESEARCH FOUNDATION
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Research Foundation
        </div>

        <div class="section-description">
            The dataset and machine-learning foundation of the project.
        </div>

        <div class="info-box">

            <strong>NHANES 2015–2018</strong>

            <br><br>

            CardioSense AI was developed using adult participant
            data from the National Health and Nutrition Examination
            Survey. The pipeline combines preprocessing, clinical
            feature engineering, advanced tabular learning,
            probability-based ensemble prediction, threshold
            optimization and SHAP explainability.

        </div>
        """
    )


    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    st.html(
        """
        <div class="disclaimer">

            <strong>⚠️ Research & Educational Use</strong>

            <br><br>

            CardioSense AI is an experimental research and
            educational tool. It is not a medical diagnostic
            device and should not replace evaluation or advice
            from a qualified healthcare professional.

        </div>
        """
    )


# ============================================================
# RISK CALCULATOR
# ============================================================

elif navigation == "🩺 Risk Calculator":

    st.html("""
        <div class="page-header">

            <div class="page-header-title">
                🩺 Cardiovascular Risk Assessment
            </div>

            <div class="page-header-text">
                Enter the patient's clinical measurements and
                biomarkers. CardioSense AI will process the data
                through its hybrid machine-learning ensemble.
            </div>

        </div>
    """)

    st.write("")


    # ========================================================
    # PATIENT INFORMATION
    # ========================================================

    st.html("""
    <div class="calculator-card">

        <div class="section-title" style="margin-top:0;">
            👤 Patient Information
        </div>

        <div class="section-description">
            Basic demographic and body measurements.
        </div>

    </div>
""")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        age = st.number_input(
            "Age",
            min_value=20,
            max_value=120,
            value=55,
            step=1,
            help="Age in years."
        )

    with c2:
        gender = st.selectbox(
            "Gender",
            ["Female", "Male"]
        )

    with c3:
        bmi = st.number_input(
            "BMI",
            min_value=10.0,
            max_value=70.0,
            value=28.5,
            step=0.1,
            format="%.1f",
            help="Body Mass Index."
        )

    with c4:
        waist = st.number_input(
            "Waist Circumference (cm)",
            min_value=40.0,
            max_value=200.0,
            value=95.0,
            step=0.5,
            format="%.1f"
        )


    # ========================================================
    # VITAL SIGNS
    # ========================================================

    st.html("""
        <div class="section-title">
            Vital Signs
        </div>

        <div class="section-description">
            Cardiovascular measurements used by the prediction pipeline.
        </div>
    """)

    c1, c2, c3 = st.columns(3)

    with c1:
        sys_bp = st.number_input(
            "Systolic Blood Pressure (mmHg)",
            min_value=70,
            max_value=250,
            value=135,
            step=1
        )

    with c2:
        dia_bp = st.number_input(
            "Diastolic Blood Pressure (mmHg)",
            min_value=40,
            max_value=150,
            value=85,
            step=1
        )

    with c3:
        pulse = st.number_input(
            "Pulse Rate (bpm)",
            min_value=30,
            max_value=220,
            value=72,
            step=1
        )


    # ========================================================
    # BIOMARKERS
    # ========================================================

    st.html("""
        <div class="section-title">
            Metabolic & Inflammatory Biomarkers
        </div>

        <div class="section-description">
            Laboratory measurements used by the CardioSense AI model.
        </div>
    """)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        total_chol = st.number_input(
            "Total Cholesterol (mg/dL)",
            min_value=50.0,
            max_value=500.0,
            value=210.0,
            step=1.0
        )

    with c2:
        hdl = st.number_input(
            "HDL Cholesterol (mg/dL)",
            min_value=10.0,
            max_value=150.0,
            value=45.0,
            step=1.0
        )

    with c3:
        hba1c = st.number_input(
            "HbA1c (%)",
            min_value=3.0,
            max_value=20.0,
            value=5.8,
            step=0.1,
            format="%.1f"
        )

    with c4:
        hs_crp = st.number_input(
            "hs-CRP (mg/L)",
            min_value=0.0,
            max_value=100.0,
            value=3.5,
            step=0.1,
            format="%.1f"
        )


    # ========================================================
    # PATIENT SUMMARY
    # ========================================================

    st.html("""
        <div class="section-title">
            Assessment Summary
        </div>
    """)

    summary1, summary2, summary3 = st.columns(3)

    with summary1:
        st.metric("Age", f"{age} years")

    with summary2:
        st.metric("BMI", f"{bmi:.1f}")

    with summary3:
        st.metric("Blood Pressure", f"{sys_bp}/{dia_bp} mmHg")


    st.write("")


    # ========================================================
    # PREDICT BUTTON
    # ========================================================

    predict_clicked = st.button(
    "🩺  Calculate Cardiovascular Risk",
    use_container_width=True
)


    if predict_clicked:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        errors = []

        if dia_bp >= sys_bp:
            errors.append(
                "Diastolic blood pressure should be lower than systolic blood pressure."
            )

        if hdl >= total_chol:
            errors.append(
                "HDL cholesterol should normally be lower than total cholesterol."
            )

        if errors:

            for error in errors:
                st.error(error)

        else:

            # ------------------------------------------------
            # CONVERT GENDER
            # ------------------------------------------------

            gender_value = 1.0 if gender == "Male" else 0.0


            # ------------------------------------------------
            # PATIENT DATA
            # ------------------------------------------------

            patient = {

                "age": float(age),

                "gender": gender_value,

                "bmi": float(bmi),

                "waist_circumference": float(waist),

                "sys_bp": float(sys_bp),

                "dia_bp": float(dia_bp),

                "pulse_rate": float(pulse),

                "tot_chol": float(total_chol),

                "hdl_chol": float(hdl),

                "hba1c": float(hba1c),

                "hs_crp": float(hs_crp),
            }


            # ------------------------------------------------
            # MODEL PREDICTION
            # ------------------------------------------------

            with st.spinner(
                "Running CardioSense AI ensemble..."
            ):

                try:

                    result = predictor.predict(patient)

                    st.session_state["prediction_result"] = result
                    st.session_state["patient_data"] = patient

                except Exception as e:

                    st.error(
                        f"Prediction failed: {str(e)}"
                    )

                    st.stop()


    # ========================================================
    # RESULTS
    # ========================================================

    if "prediction_result" in st.session_state:

        result = st.session_state["prediction_result"]

        st.divider()

        st.html("""
            <div class="section-title">
                Cardiovascular Risk Result
            </div>

            <div class="section-description">
                Prediction generated by the CardioSense AI hybrid ensemble.
            </div>
        """)


        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        risk = float(result["probability"])

        risk_percent = float(result["risk_percent"])


        if risk_percent < 10:
            risk_status = "Lower estimated risk"
            risk_color = "#059669"
        elif risk_percent < 20:
            risk_status = "Moderate estimated risk"
            risk_color = "#d97706"
        else:
            risk_status = "Higher estimated risk"
            risk_color = "#dc2626"

        gauge_pct = min(max(risk_percent, 0.0), 100.0)

        st.html(
            f"""
            <div class="risk-result-card">

                <div class="risk-result-label">
                    Estimated CVD Risk &nbsp;•&nbsp; Ensemble Probability
                </div>

                <div class="risk-result-value" style="color:{risk_color};">
                    {risk_percent:.2f}%
                </div>

                <div class="risk-status-tag" style="color:{risk_color};">
                    {risk_status}
                </div>

                <div class="risk-gauge-track">
                    <div class="risk-gauge-fill" style="width:{gauge_pct}%; background:{risk_color};"></div>
                </div>

                <div class="risk-gauge-scale">
                    <span>0%</span>
                    <span>25%</span>
                    <span>50%</span>
                    <span>75%</span>
                    <span>100%</span>
                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # INDIVIDUAL MODELS
        # ----------------------------------------------------

        st.html("""
            <div class="section-title">
                Individual Model Predictions
            </div>

            <div class="section-description">
                Each model's independent probability before ensemble weighting.
            </div>
        """)


        model_predictions = result.get("models", {})

        model_weights = predictor.ensemble_config.get("weights", {})

        if model_predictions:

            cols = st.columns(len(model_predictions))

            for column, (model, probability) in zip(
                cols,
                model_predictions.items()
            ):

                with column:

                    weight_pct = model_weights.get(model, 0) * 100

                    st.html(
                        f"""
                        <div class="model-pred-card">
                            <div class="model-pred-name">{model}</div>
                            <div class="model-pred-value">{float(probability) * 100:.2f}%</div>
                            <div class="model-pred-weight">Ensemble weight: {weight_pct:.0f}%</div>
                        </div>
                        """
                    )


        # ----------------------------------------------------
        # THRESHOLD DECISIONS
        # ----------------------------------------------------

        st.html("""
            <div class="section-title">
                Decision Thresholds
            </div>

            <div class="section-description">
                The same probability can be interpreted using
                different clinically-calibrated operating thresholds.
            </div>
        """)


        threshold_decisions = result.get("decisions", {})
        thresholds = result.get("thresholds", {})

        threshold_labels = {
            "default": "Default",
            "optimal_f1": "Optimal F1",
            "high_precision": "High Precision",
            "clinical_screening": "Clinical Screening",
        }

        if threshold_decisions:

            t_cols = st.columns(len(threshold_decisions))

            for column, key in zip(t_cols, threshold_decisions.keys()):

                decision = threshold_decisions[key]
                threshold_value = thresholds.get(key, 0)
                label = threshold_labels.get(key, key)

                status_text = "POSITIVE" if decision else "NEGATIVE"
                status_class = "positive" if decision else "negative"

                with column:

                    st.html(
                        f"""
                        <div class="threshold-card {status_class}">
                            <div class="threshold-name">{label}</div>
                            <div class="threshold-cutoff">Cutoff: {threshold_value * 100:.1f}%</div>
                            <div class="threshold-status">{status_text}</div>
                        </div>
                        """
                    )


        # ----------------------------------------------------
        # DISCLAIMER
        # ----------------------------------------------------

        st.html(
            """
            <div class="disclaimer">
                <strong>⚠️ Not a Medical Diagnosis</strong>
                <br><br>
                This result is generated by an experimental research
                model and is not a medical diagnosis. Consult a
                qualified healthcare professional for clinical evaluation.
            </div>
            """
        )


# ============================================================
# AI MODEL
# ============================================================

elif navigation == "🧠 AI Models":

    st.html(
        """
        <div class="page-header">

            <div class="page-header-title">
                🧠 CardioSense AI Models
            </div>

            <div class="page-header-text">
                Five complementary machine-learning and deep-learning
                models, each independently trained on the same 20
                clinical and engineered features, combined into a
                single hybrid ensemble.
            </div>

        </div>
        """
    )

    st.write("")

    model_cards = [
        (
            "🌳", "LightGBM",
            "A gradient-boosted decision tree model optimized for "
            "speed and accuracy on structured, tabular clinical data. "
            "Builds trees leaf-wise to capture nonlinear feature "
            "interactions efficiently.",
            "Gradient Boosting",
        ),
        (
            "🌲", "XGBoost",
            "A second, independently regularized gradient-boosting "
            "implementation. Its different tree-growth and "
            "regularization strategy makes it a complementary "
            "signal to LightGBM rather than a duplicate.",
            "Gradient Boosting",
        ),
        (
            "🧩", "FT-Transformer",
            "Feature Tokenizer + Transformer: each clinical feature "
            "is embedded into its own token, then passed through "
            "self-attention blocks so the model can learn which "
            "combinations of features matter most.",
            "Transformer (Tabular)",
        ),
        (
            "🔀", "SAINT",
            "Self-Attention and Intersample Attention for Tabular "
            "data. In addition to attending across a patient's own "
            "features, SAINT attends across other patients in the "
            "batch, capturing relative/contextual risk patterns.",
            "Attention-Based",
        ),
        (
            "🕸️", "PyTorch Deep Tabular",
            "A residual feed-forward neural network (TabularResNet) "
            "with batch normalization and skip connections, "
            "providing a classic deep-learning perspective on the "
            "same tabular inputs.",
            "Deep Neural Network",
        ),
    ]

    m_cols = st.columns(3)

    for i, (icon, name, desc, tag) in enumerate(model_cards):

        with m_cols[i % 3]:

            st.html(
                f"""
                <div class="model-card">
                    <div class="model-card-icon">{icon}</div>
                    <div class="model-card-title">{name}</div>
                    <div class="model-card-text">{desc}</div>
                    <div class="model-card-tag">{tag}</div>
                </div>
                """
            )

            st.write("")


    # --------------------------------------------------------
    # HYBRID ENSEMBLE
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Hybrid Probability Ensemble
        </div>

        <div class="section-description">
            Each model outputs an independent probability. CardioSense
            AI combines them into one final risk estimate using a
            fixed, validation-optimized weighted average — not a
            simple majority vote.
        </div>
        """
    )

    weights = predictor.ensemble_config["weights"]

    weights_html = '<div class="calculator-card">'

    for model_name, weight in weights.items():

        pct = weight * 100

        weights_html += f"""
            <div class="weight-row">
                <div class="weight-name">{model_name}</div>
                <div class="weight-track">
                    <div class="weight-fill" style="width:{pct}%;"></div>
                </div>
                <div class="weight-pct">{pct:.0f}%</div>
            </div>
        """

    weights_html += "</div>"

    st.html(weights_html)

    st.html(
        """
        <div class="info-box" style="margin-top:20px;">
            <strong>How the final probability is calculated</strong>
            <br><br>
            final_probability =
            0.25 × LightGBM + 0.25 × XGBoost + 0.20 × FT&#8209;Transformer
            + 0.15 × SAINT + 0.15 × PyTorch&nbsp;Deep&nbsp;Tabular
            <br><br>
            The tree-based models (LightGBM, XGBoost) carry the
            largest combined weight (50%), reflecting their strong,
            well-established performance on structured clinical
            data, while the three neural architectures contribute
            complementary, nonlinear representations of the same
            features.
        </div>
        """
    )

    st.html(
        """
        <div class="disclaimer" style="background:#eff6ff; border-color:#bfdbfe; color:#1e3a8a;">
            <strong>ℹ️ A note on "best" models</strong>
            <br><br>
            This page does not label any single model as the
            "best" performer. Ranking models by accuracy, AUC or
            F1 requires stored evaluation results from the original
            training/validation pipeline; CardioSense AI instead
            treats all five models as complementary contributors
            to one calibrated ensemble estimate.
        </div>
        """
    )


# ============================================================
# EXPLAINABILITY
# ============================================================

elif navigation == "🔬 Explainability":

    st.html(
        """
        <div class="page-header">

            <div class="page-header-title">
                🔬 Explainable AI
            </div>

            <div class="page-header-text">
                Understand which clinical and biomarker features
                push a prediction toward higher or lower estimated
                cardiovascular risk.
            </div>

        </div>
        """
    )

    st.write("")

    # --------------------------------------------------------
    # WHAT / WHY
    # --------------------------------------------------------

    e1, e2 = st.columns(2)

    with e1:
        st.html(
            """
            <div class="feature-card" style="min-height:170px;">
                <div class="feature-icon">❓</div>
                <div class="feature-title">What is Explainable AI?</div>
                <div class="feature-description">
                    Explainable AI (XAI) refers to techniques that
                    describe <em>why</em> a model produced a given
                    output, rather than treating the model as an
                    opaque black box. In a clinical context, this
                    lets a prediction be inspected rather than
                    simply trusted.
                </div>
            </div>
            """
        )

    with e2:
        st.html(
            """
            <div class="feature-card" style="min-height:170px;">
                <div class="feature-icon">🧮</div>
                <div class="feature-title">Why SHAP?</div>
                <div class="feature-description">
                    SHAP (SHapley Additive exPlanations) assigns
                    each input feature a signed contribution to a
                    specific prediction, grounded in cooperative
                    game theory. Contributions are additive: the
                    baseline plus every feature's contribution
                    reconstructs the model's output exactly.
                </div>
            </div>
            """
        )

    st.write("")

    st.html(
        """
        <div class="info-box">
            <strong>How CardioSense AI explains predictions</strong>
            <br><br>
            Two complementary views are shown below. <strong>Global
            importance</strong> uses the gain-based feature
            importance already stored inside the trained LightGBM
            and XGBoost boosters — a direct, honest read of what
            those models learned, with no extra computation needed.
            <strong>Individual explanation</strong> computes real
            SHAP values (via <code>shap.KernelExplainer</code>) for
            one patient at a time, treating the entire five-model
            hybrid ensemble as the function being explained — so the
            attribution reflects the actual deployed prediction, not
            just one sub-model.
        </div>
        """
    )


    # --------------------------------------------------------
    # GLOBAL FEATURE IMPORTANCE
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Global Feature Importance
        </div>

        <div class="section-description">
            Gain-based importance from the trained LightGBM and
            XGBoost models, blended with equal weight.
        </div>
        """
    )

    try:
        importance_rows = explainability.get_global_importance(predictor, top_n=12)
        max_importance = max(r["importance"] for r in importance_rows) or 1.0

        bars_html = '<div class="calculator-card">'
        for row in importance_rows:
            width_pct = (row["importance"] / max_importance) * 100
            bars_html += f"""
                <div class="importance-row">
                    <div class="importance-name">{row['feature']}</div>
                    <div class="importance-track">
                        <div class="importance-fill" style="width:{width_pct:.1f}%;"></div>
                    </div>
                </div>
            """
        bars_html += "</div>"

        st.html(bars_html)

    except Exception as e:
        st.error("Global feature importance could not be computed.")
        with st.expander("Technical details (for developers)"):
            st.code(str(e))


    # --------------------------------------------------------
    # INDIVIDUAL PREDICTION EXPLANATION
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Individual Prediction Explanation
        </div>

        <div class="section-description">
            SHAP attribution for one specific patient's ensemble
            probability.
        </div>
        """
    )

    patient_for_explanation = st.session_state.get("patient_data")

    if patient_for_explanation is None:

        st.html(
            """
            <div class="info-box">
                Run the <strong>Risk Calculator</strong> first to
                generate a prediction — this page will then explain
                that specific patient's result.
            </div>
            """
        )

        demo_clicked = st.button(
            "Explain a sample cohort-average patient instead",
            use_container_width=True,
        )

        if demo_clicked:
            reference = explainability.get_reference_patient(predictor)
            patient_for_explanation = {
                "age": reference["age"],
                "gender": 1.0,
                "bmi": reference["bmi"],
                "waist_circumference": reference["waist_circumference"],
                "sys_bp": reference["sys_bp"],
                "dia_bp": reference["dia_bp"],
                "pulse_rate": reference["pulse_rate"],
                "tot_chol": reference["tot_chol"],
                "hdl_chol": reference["hdl_chol"],
                "hba1c": reference["hba1c"],
                "hs_crp": reference["hs_crp"],
            }
            st.caption(
                "Showing a demo explanation for the cohort-average "
                "patient (real NHANES-derived feature means), not a "
                "specific individual."
            )

    else:
        st.html(
            """
            <div class="info-box">
                Explaining the most recently calculated prediction
                from the Risk Calculator page.
            </div>
            """
        )

    if patient_for_explanation is not None:

        with st.spinner("Computing SHAP attribution across the ensemble..."):

            try:
                explanation = explainability.explain_prediction(
                    predictor,
                    patient_for_explanation,
                    nsamples=150,
                )

                base = explanation["base_value"]
                contributions = explanation["contributions"]
                max_abs = max(abs(c["value"]) for c in contributions) or 1.0

                st.caption(
                    f"Baseline (cohort-average) probability: "
                    f"{base * 100:.2f}%  →  "
                    f"Explained prediction: "
                    f"{explanation['predicted_value'] * 100:.2f}%"
                )

                shap_html = '<div class="calculator-card">'

                for c in contributions:

                    direction = "increase" if c["value"] >= 0 else "decrease"
                    bar_pct = (abs(c["value"]) / max_abs) * 50

                    if direction == "increase":
                        left = 50
                        style = f"left:{left}%; width:{bar_pct:.1f}%;"
                    else:
                        left = 50 - bar_pct
                        style = f"left:{left:.1f}%; width:{bar_pct:.1f}%;"

                    shap_html += f"""
                        <div class="shap-row">
                            <div class="shap-name">
                                {c['feature']}
                                <div class="shap-name-value">value: {c['patient_value']}</div>
                            </div>
                            <div class="shap-bar-area">
                                <div class="shap-bar-center"></div>
                                <div class="shap-bar-fill {direction}" style="{style}"></div>
                            </div>
                            <div class="shap-value-label {direction}">
                                {'+' if c['value'] >= 0 else ''}{c['value']*100:.2f}%
                            </div>
                        </div>
                    """

                shap_html += "</div>"

                st.html(shap_html)

                st.html(
                    """
                    <div style="margin-top:14px; font-size:12.5px; color:#64748b;">
                        <span class="legend-dot" style="background:#f87171;"></span>
                        Increases estimated risk
                        &nbsp;&nbsp;&nbsp;
                        <span class="legend-dot" style="background:#34d399;"></span>
                        Decreases estimated risk
                    </div>
                    """
                )

            except RuntimeError as e:
                st.warning(str(e))

            except Exception as e:
                st.error(
                    "The individual prediction explanation could "
                    "not be computed."
                )
                with st.expander("Technical details (for developers)"):
                    st.code(str(e))


# ============================================================
# METHODOLOGY
# ============================================================

elif navigation == "⚙️ Methodology":

    st.html(
        """
        <div class="page-header">

            <div class="page-header-title">
                ⚙️ Methodology
            </div>

            <div class="page-header-text">
                The complete CardioSense AI pipeline, from raw
                NHANES survey data to an explainable cardiovascular
                risk estimate.
            </div>

        </div>
        """
    )

    st.write("")


    # --------------------------------------------------------
    # DATASET / CLASS IMBALANCE
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Research Foundation &amp; Dataset
        </div>

        <div class="section-description">
            NHANES 2015–2018, adult participants with valid
            cardiovascular disease outcome data.
        </div>
        """
    )

    d1, d2, d3 = st.columns(3)

    with d1:
        st.html(
            """
            <div class="stat-card">
                <div class="stat-number">11,286</div>
                <div class="stat-label">Adult participants with valid CVD target data</div>
            </div>
            """
        )

    with d2:
        st.html(
            """
            <div class="stat-card">
                <div class="stat-number">1,198</div>
                <div class="stat-label">CVD-positive participants (≈10.61%)</div>
            </div>
            """
        )

    with d3:
        st.html(
            """
            <div class="stat-card">
                <div class="stat-number">10,088</div>
                <div class="stat-label">CVD-negative participants (≈89.39%)</div>
            </div>
            """
        )

    st.html(
        """
        <div class="calculator-card">
            <div class="section-title" style="margin-top:0; font-size:16px;">
                Class Balance
            </div>
            <div class="class-balance-track">
                <div class="class-balance-negative" style="width:89.39%;">89.39% negative</div>
                <div class="class-balance-positive" style="width:10.61%;">10.61%</div>
            </div>
            <div class="section-description" style="margin-bottom:0;">
                CVD is a minority class. This imbalance directly
                motivates the multiple decision thresholds shown on
                the Risk Calculator page — a single 50% cutoff
                would under-flag positive cases in a screening
                context.
            </div>
        </div>
        """
    )


    # --------------------------------------------------------
    # PIPELINE STEPS
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            End-to-End Pipeline
        </div>
        """
    )

    steps = [
        (
            "1", "NHANES 2015–2018 Raw Survey Data",
            "Demographic, examination and laboratory data for adult "
            "participants across two NHANES cycles are merged into "
            "a single modeling population of 11,286 records."
        ),
        (
            "2", "Data Preprocessing",
            "Missing numeric values are imputed with a median "
            "imputer, then all 19 numeric features are standardized "
            "with a StandardScaler fit on the training population. "
            "Gender is encoded separately as a binary is_male flag."
        ),
        (
            "3", "Clinical Feature Engineering",
            "From the 11 raw inputs, 9 engineered features are "
            "derived: pulse pressure, mean arterial pressure, "
            "cholesterol/HDL ratio, non-HDL cholesterol, log "
            "hs-CRP, a CRP high-risk flag, an age–BMI risk index, "
            "a cardio-inflammatory index and a metabolic-age index — "
            "bringing the model input to 20 total features."
        ),
        (
            "4", "Model Training",
            "Five models — LightGBM, XGBoost, FT-Transformer, "
            "SAINT and a PyTorch TabularResNet — are trained "
            "independently on the same 20-feature representation, "
            "each learning a different inductive bias over the "
            "same clinical signal."
        ),
        (
            "5", "Probability Ensemble",
            "The five models' output probabilities are combined "
            "using a fixed, validation-optimized weighted average "
            "(25% / 25% / 20% / 15% / 15%) rather than a simple "
            "vote, favoring the tree-based models while retaining "
            "the neural models' complementary signal."
        ),
        (
            "6", "Threshold Optimization",
            "Because CVD-positive cases are a minority (~10.6%), a "
            "single 0.50 cutoff is often too conservative for "
            "screening. Four operating thresholds are stored "
            "alongside the ensemble: Default, Optimal F1, High "
            "Precision and Clinical Screening."
        ),
        (
            "7", "Explainable Risk Output",
            "The final probability is paired with SHAP-based "
            "explanations — global gain-based importance from the "
            "tree models, and per-patient KernelExplainer "
            "attribution across the full ensemble — so a prediction "
            "can be inspected, not just trusted."
        ),
    ]

    for number, title, text in steps:
        st.html(
            f"""
            <div class="method-step">
                <div class="method-step-number">{number}</div>
                <div>
                    <div class="method-step-title">{title}</div>
                    <div class="method-step-text">{text}</div>
                </div>
            </div>
            """
        )


    # --------------------------------------------------------
    # NOTE ON TRAIN/VAL/TEST SPLIT
    # --------------------------------------------------------

    st.html(
        """
        <div class="info-box" style="margin-top:10px;">
            <strong>On the train / validation / test split</strong>
            <br><br>
            The exact split ratio used during model development is
            not stored in this deployment's configuration files
            (only the trained artifacts, scaler, imputer and
            ensemble weights are shipped here). What is confirmed
            by the shipped configuration is that class imbalance
            (~10.61% positive) was explicitly accounted for through
            threshold optimization rather than left to a default
            0.50 cutoff alone.
        </div>
        """
    )


    # --------------------------------------------------------
    # THRESHOLDS TABLE
    # --------------------------------------------------------

    st.html(
        """
        <div class="section-title">
            Stored Decision Thresholds
        </div>
        """
    )

    thresholds = predictor.ensemble_config["thresholds"]
    threshold_labels = {
        "default": ("Default", "Standard 50% cutoff."),
        "optimal_f1": ("Optimal F1", "Balances precision and recall on the validation set."),
        "high_precision": ("High Precision", "Minimizes false positives."),
        "clinical_screening": ("Clinical Screening", "Lower cutoff to favor sensitivity, catching more true positives."),
    }

    th_cols = st.columns(4)
    for col, (key, (label, desc)) in zip(th_cols, threshold_labels.items()):
        with col:
            st.html(
                f"""
                <div class="threshold-card">
                    <div class="threshold-name">{label}</div>
                    <div class="threshold-cutoff">{thresholds[key]*100:.1f}%</div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:6px;">{desc}</div>
                </div>
                """
            )

    st.html(
        """
        <div class="disclaimer">
            <strong>⚠️ Research & Educational Use</strong>
            <br><br>
            CardioSense AI is an experimental research and
            educational tool. It is not a medical diagnostic
            device and should not replace evaluation or advice
            from a qualified healthcare professional.
        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.html(
    """
    <div class="footer-text">

        <strong>CardioSense AI</strong>
        <br>

        Explainable Cardiovascular Risk Prediction
        <br>

        Academic Research Project

    </div>
    """
)