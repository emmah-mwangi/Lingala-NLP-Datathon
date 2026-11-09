"""Streamlit demo - Team 07 Datalynk | Lingala Intent Classification
Strathmore NLP Hub Datathon 2026 | Track A: intent classification

Entry point:
    python -m streamlit run app.py

The app degrades gracefully when the model has not yet been trained: the
backend availability indicator stays visible, the text input stays usable,
and the classify action reports a clear error instead of raising. Empty
input is handled explicitly before any call to the prediction backend.
"""

from __future__ import annotations

import streamlit as st

from nlp.availability import probe_status
from nlp.config import (
    DATATHON_NAME,
    SUPPORTED_TRACKS,
    TEAM_NAME,
    TEAM_NUMBER,
    TARGET_LANGUAGE,
)
from nlp.predictor import predict
from nlp.summary import load_contribution, summary
from nlp.ui import build_disclaimer, confidence_band, format_probability

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=f"Team {TEAM_NUMBER} {TEAM_NAME} - {TARGET_LANGUAGE} NLP Demo",
    page_icon="",
    layout="centered",
)

st.title(f"{TARGET_LANGUAGE} Intent Classifier")
st.caption(
    f"Team {TEAM_NUMBER} · {TEAM_NAME} · {DATATHON_NAME} · Track A — Intent Classification"
)

# ---------------------------------------------------------------------------
# Prototype status banner
# ---------------------------------------------------------------------------
st.badge("Prototype", icon=":material/science:")
st.write(
    "This is a small-data research prototype. Development-set scores are "
    "teaching figures, not a production benchmark."
)

st.divider()

# ---------------------------------------------------------------------------
# Dataset summary (verified figures only; target vs achieved kept distinct)
# ---------------------------------------------------------------------------
summary_data = summary()

with st.expander("Dataset summary", expanded=True):
    if not summary_data["exists"]:
        st.warning(
            "No contribution data found at "
            f"`{summary_data['path']}`. Run `python ingest_batch.py` first."
        )
    else:
        st.write(
            f"**Language:** {summary_data['language']} · "
            f"**Accepted records:** {summary_data['total']}"
        )

        st.write("**Batch milestones** (target vs achieved):")
        for item in summary_data["batch_progress"]:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{item['name']}: {item['achieved']}/{item['target']}")
            col_b.write("reached" if item["reached"] else "not reached")

        st.write("**Per-label progress** (target 25 each):")
        for item in summary_data["label_progress"]:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{item['label']}: {item['achieved']}/{item['target']}")
            col_b.write("reached" if item["reached"] else "shortfall")

        st.write("**Volunteer allocation** (test records):")
        for item in summary_data["volunteer_progress"]:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{item['code']}: {item['achieved']}/{item['target']}")
            col_b.write("reached" if item["reached"] else "shortfall")

        st.write("**Review coverage:**")
        for label, count in summary_data["review_coverage"].items():
            st.write(f"- {label}: {count}")

st.divider()

# ---------------------------------------------------------------------------
# Model / backend availability indicator
# ---------------------------------------------------------------------------
track = st.selectbox("Task", SUPPORTED_TRACKS, index=0)
status = probe_status(track)

if status["available"]:
    pack = status["pack"]
    st.success(
        f"**Backend available** — track `{track}`, language "
        f"`{pack['language']}`. Artefacts present: "
        + ", ".join(
            f"{name}={state}" for name, state in status["artefacts"].items()
        )
    )
    if pack["practice"]:
        st.warning(
            "PRACTICE MODE — constructed teaching examples. Scores do not "
            "establish real-world quality."
        )
else:
    st.error(
        f"**Backend not available** for track `{track}`. "
        f"{status['error']}"
    )
    pack = None

st.divider()

# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
st.write(f"Enter a sentence in **{TARGET_LANGUAGE}**:")

EXAMPLES = [
    "Tala mbula lelo.",
    "Ngonga ezali ngonga nini?",
    "Bongisa kengele na ngonga motoba.",
    "Nalingi alarme ebeta na ngonga ya sambo.",
    "Tya rendez-vous na calendrier na ngai mpo na mokolo ya mibale.",
]
cols = st.columns(len(EXAMPLES))
for col, example in zip(cols, EXAMPLES):
    if col.button(example, key=f"example_{example[:20]}"):
        st.session_state["lingala_input"] = example

text = st.text_area(
    "Lingala sentence",
    value=st.session_state.get("lingala_input", ""),
    key="lingala_input",
    height=80,
)

if st.button("Classify", type="primary"):
    if not text or not text.strip():
        st.info("Enter some text first, then classify.")
        st.stop()

    if pack is None:
        st.error(
            f"Cannot classify: backend for track `{track}` is not available. "
            f"{status['error']}"
        )
        st.stop()

    try:
        result = predict(text, pack)
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    st.subheader(f"Predicted intent: {result.friendly_label}")
    st.write(
        f"Model probability (uncalibrated): **{format_probability(result.probability)}** "
        f"({confidence_band(result.probability)})"
    )
    st.caption(
        "This score is not a guarantee of correctness. The model always "
        "chooses a known label, even for unsupported input."
    )
    st.info(build_disclaimer(track))