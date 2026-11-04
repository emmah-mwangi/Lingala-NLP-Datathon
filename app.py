"""
Streamlit demo — Team 07 Datalynk | Lingala Intent Classification
Strathmore NLP Hub Datathon 2026

Entry point:
    python -m streamlit run app.py

The app degrades gracefully when the model has not yet been trained:
it shows a clear instruction and stops rather than raising an exception.
"""

import json

import streamlit as st

from nlp.config import (
    DATATHON_NAME,
    SUPPORTED_TRACKS,
    TEAM_NAME,
    TEAM_NUMBER,
    TARGET_LANGUAGE,
)
from nlp.data_loader import ModelNotTrainedError, load_dev_metrics, load_model_pack
from nlp.predictor import predict
from nlp.utils import format_probability

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"Team {TEAM_NUMBER} {TEAM_NAME} — {TARGET_LANGUAGE} NLP Demo",
    page_icon="🌍",
)

st.title(f"🌍 {TARGET_LANGUAGE} NLP Demo")
st.caption(f"Team {TEAM_NUMBER} · {TEAM_NAME} · {DATATHON_NAME}")

# ── Track selection ───────────────────────────────────────────────────────────
track = st.selectbox("Task", SUPPORTED_TRACKS)

# ── Model loading ─────────────────────────────────────────────────────────────
try:
    pack = load_model_pack(track)
except ModelNotTrainedError as exc:
    st.info(str(exc))
    st.stop()

if pack["practice"]:
    st.warning(
        "⚠️ PRACTICE MODE — constructed English teaching examples. "
        "Scores do not establish real-world quality."
    )

st.write(f"**Model language:** {pack['language']}")

# ── Dev metrics (shown when available, never fabricated) ──────────────────────
dev = load_dev_metrics(track)
if dev:
    col1, col2 = st.columns(2)
    col1.metric("Dev accuracy", f"{dev['model']['accuracy']:.3f}")
    col2.metric("Dev macro-F1", f"{dev['model']['macro_f1']:.3f}")
    st.caption(
        "Development-set scores only. Do not tune against these after freezing. "
        "Final test scores are in test_metrics.json."
    )

st.divider()

# ── Prediction ────────────────────────────────────────────────────────────────
text = st.text_area(f"Enter text in {pack['language']}")

if st.button("Predict"):
    if not text.strip():
        st.info("Enter some text first.")
        st.stop()

    try:
        result = predict(text, pack)
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    if track == "sentiment":
        st.subheader(f"The sentiment is: {result.friendly_label}")
    else:
        st.subheader(f"The intention of the user is: {result.friendly_label}")

    st.write(f"Model probability (uncalibrated): **{format_probability(result.probability)}**")
    st.caption(
        "This score is not a guarantee of correctness. "
        "The model always chooses a known label, even for unsupported input."
    )

    if track == "semantic":
        st.json({"intent": result.label, "slots": result.slots})
        st.caption(
            "Training-only surface-value matcher: unseen slot values may be missed. "
            "No date/time normalisation or real action is executed."
        )
    elif track == "intent":
        st.info(
            "Simulated route only. No calendar, music, weather or other "
            "external action has been executed."
        )
    else:
        st.info(
            "Sentence-level opinion label only. "
            "This is not emotion detection, sarcasm understanding or a diagnosis."
        )
