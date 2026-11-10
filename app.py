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

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from nlp.availability import probe_status
from nlp.config import (
    DATATHON_NAME,
    SUPPORTED_TRACKS,
    TEAM_NAME,
    TEAM_NUMBER,
    TARGET_LANGUAGE,
    artifact_dir,
)
from nlp.data_loader import load_test_predictions
from nlp.predictor import predict
from nlp.summary import load_contribution, summary
from nlp.ui import build_disclaimer, confidence_band, format_probability

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=f"Team {TEAM_NUMBER} {TEAM_NAME} - {TARGET_LANGUAGE} NLP Demo",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar: Project Identity
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Project Identity")
    st.markdown(f"""
    **Team:** {TEAM_NUMBER} — {TEAM_NAME}  
    **Language:** {TARGET_LANGUAGE}  
    **Track:** A — Intent Classification  
    **Event:** {DATATHON_NAME}
    """)
    st.divider()
    st.subheader("Prototype Status")
    st.warning(
        "⚠️ **Research Prototype**\n\n"
        "This is a small-data research prototype developed for the Strathmore "
        "NLP Hub Datathon 2026. Development-set scores are teaching figures, "
        "not a production benchmark. The model is trained on ~250 Lingala "
        "sentences across 10 intent classes. Predictions on unseen data "
        "may be unreliable."
    )
    st.divider()
    st.caption("Built with Streamlit • scikit-learn • pandas")

# ---------------------------------------------------------------------------
# Main: Title and Caption
# ---------------------------------------------------------------------------
st.title(f"{TARGET_LANGUAGE} Intent Classifier")
st.caption(
    f"Team {TEAM_NUMBER} · {TEAM_NAME} · {DATATHON_NAME} · Track A — Intent Classification"
)

# ---------------------------------------------------------------------------
# Section 1: Intent Classifier (Interactive Prediction)
# ---------------------------------------------------------------------------
st.header("1. Intent Classifier")

# Load Lingala examples from the actual dataset
@st.cache_data
def get_lingala_examples() -> list[dict[str, str]]:
    """Extract example sentences from the contribution CSV with their labels."""
    df = load_contribution()
    if df.empty:
        return []
    # Get a diverse set: one per label, preferring independently_reviewed
    examples = []
    for label in df["label"].unique():
        subset = df[(df["label"] == label) & (df["review_status"] == "independently_reviewed")]
        if subset.empty:
            subset = df[df["label"] == label]
        if not subset.empty:
            row = subset.iloc[0]
            examples.append({
                "text": row["text"],
                "label": row["label"],
                "meaning": FRIENDLY_MEANINGS.get(row["label"], row["label"])
            })
    return examples

# Friendly meanings for the 10 intent labels
FRIENDLY_MEANINGS = {
    "weather_query": "Ask about weather conditions",
    "datetime_query": "Ask for current date or time",
    "alarm_set": "Set an alarm to ring",
    "calendar_set": "Create a calendar event",
    "calendar_query": "Ask about existing calendar events",
    "lists_createoradd": "Create a list or add items",
    "lists_query": "Read an existing list",
    "play_music": "Request music playback",
    "news_query": "Ask for news updates",
    "qa_definition": "Ask for the meaning of a word or concept",
}

lingala_examples = get_lingala_examples()

# Track selection and backend status
track = st.selectbox("Task", SUPPORTED_TRACKS, index=0, key="track_select")
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
            "⚠️ **PRACTICE MODE** — constructed teaching examples (English). "
            "Scores do not establish real-world quality for Lingala."
        )
else:
    st.error(
        f"**Backend not available** for track `{track}`. "
        f"{status['error']}"
    )
    pack = None

st.divider()

# Example selection
st.write(f"Select a **{TARGET_LANGUAGE}** example or enter your own sentence:")

if lingala_examples:
    example_options = ["— Custom input —"] + [
        f"{ex['text']}  [{ex['label']}]" for ex in lingala_examples
    ]
    selected_idx = st.selectbox(
        "Examples from dataset",
        range(len(example_options)),
        format_func=lambda i: example_options[i],
        key="example_select",
    )
else:
    selected_idx = 0
    st.info("No Lingala examples available yet. Run data ingestion first.")

# Text input
default_text = ""
if selected_idx > 0 and lingala_examples:
    default_text = lingala_examples[selected_idx - 1]["text"]

text = st.text_area(
    f"Lingala sentence",
    value=st.session_state.get("lingala_input", default_text),
    key="lingala_input",
    height=100,
    placeholder=f"Type a sentence in {TARGET_LANGUAGE}...",
)

col1, col2 = st.columns([1, 1])
with col1:
    classify_clicked = st.button("Classify", type="primary", use_container_width=True)
with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state["lingala_input"] = ""
        st.rerun()

# ---------------------------------------------------------------------------
# Prediction Logic
# ---------------------------------------------------------------------------
if classify_clicked:
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
        result = predict(text.strip(), pack)
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    # Display prediction results
    st.subheader("Prediction Result")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.metric(
            label="Predicted Intent",
            value=result.friendly_label,
            help=f"Internal label: {result.label}"
        )
        st.caption(f"Raw label: `{result.label}`")
    with col_b:
        prob_pct = format_probability(result.probability)
        conf_band = confidence_band(result.probability)
        st.metric(
            label="Model Probability (uncalibrated)",
            value=prob_pct,
            delta=conf_band,
            delta_color="off",
        )

    st.caption(
        "⚠️ This score is not a guarantee of correctness. The model always "
        "chooses a known label, even for unsupported or out-of-domain input."
    )
    st.info(build_disclaimer(track))

    # Show all class probabilities if available
    if hasattr(pack["model"], "predict_proba"):
        try:
            proba = pack["model"].predict_proba([text.strip()])[0]
            classes = pack["model"].classes_
            prob_df = pd.DataFrame({
                "Intent": [FRIENDLY_MEANINGS.get(c, c) for c in classes],
                "Label": classes,
                "Probability": [format_probability(float(p)) for p in proba],
            }).sort_values("Probability", ascending=False)
            with st.expander("All class probabilities"):
                st.dataframe(prob_df, use_container_width=True, hide_index=True)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Section 2: Demonstration Examples (from evaluation artifacts)
# ---------------------------------------------------------------------------
st.divider()
st.header("2. Demonstration Examples")

st.write(
    "The following examples are drawn from the **test set evaluation** "
    "(practice model on English teaching data). They illustrate typical "
    "successes and failures. The real Lingala model evaluation will appear "
    "here once the contribution data is split and evaluated."
)

# Load test predictions for demonstration
test_preds = load_test_predictions(track)
dev_metrics_path = artifact_dir(track) / "dev_metrics.json"
test_metrics_path = artifact_dir(track) / "test_metrics.json"

demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    st.subheader("✅ Successful Predictions")
    if test_preds is not None and not test_preds.empty:
        correct = test_preds[test_preds["label"] == test_preds["predicted"]]
        for _, row in correct.head(3).iterrows():
            with st.container(border=True):
                st.write(f"**Sentence:** {row['text']}")
                st.write(f"**Expected:** {FRIENDLY_MEANINGS.get(row['label'], row['label'])} (`{row['label']}`)")
                st.write(f"**Predicted:** {FRIENDLY_MEANINGS.get(row['predicted'], row['predicted'])} (`{row['predicted']}`)")
                st.success("Correct ✓")
    else:
        st.info("No test predictions available. Run `evaluate.py` to generate them.")

with demo_col2:
    st.subheader("❌ Failure Cases")
    if test_preds is not None and not test_preds.empty:
        incorrect = test_preds[test_preds["label"] != test_preds["predicted"]]
        for _, row in incorrect.head(2).iterrows():
            with st.container(border=True):
                st.write(f"**Sentence:** {row['text']}")
                st.write(f"**Expected:** {FRIENDLY_MEANINGS.get(row['label'], row['label'])} (`{row['label']}`)")
                st.write(f"**Predicted:** {FRIENDLY_MEANINGS.get(row['predicted'], row['predicted'])} (`{row['predicted']}`)")
                st.error("Incorrect ✗")
                # Explain likely cause
                if row['label'] in ['calendar_set', 'lists_createoradd'] and row['predicted'] in ['calendar_query', 'lists_query']:
                    st.caption("Likely cause: Overlap in vocabulary between create vs query actions.")
                elif row['label'] == 'weather_query' and row['predicted'] == 'qa_definition':
                    st.caption("Likely cause: Question phrasing resembles definition queries.")
                else:
                    st.caption("Likely cause: Lexical overlap between intent classes in small training set.")
    else:
        st.info("No test predictions available. Run `evaluate.py` to generate them.")

# ---------------------------------------------------------------------------
# Section 3: Model Performance
# ---------------------------------------------------------------------------
st.divider()
st.header("3. Model Performance")

if test_metrics_path.exists():
    with open(test_metrics_path, encoding="utf-8") as f:
        test_metrics = json.load(f)
    
    model_metrics = test_metrics.get("model", {})
    baseline_metrics = test_metrics.get("majority_baseline", {})
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            "Test Accuracy",
            f"{model_metrics.get('accuracy', 0):.1%}",
            delta=f"{(model_metrics.get('accuracy', 0) - baseline_metrics.get('accuracy', 0)):.1%} vs baseline",
        )
    with col_m2:
        st.metric(
            "Macro F1",
            f"{model_metrics.get('macro_f1', 0):.3f}",
            delta=f"{(model_metrics.get('macro_f1', 0) - baseline_metrics.get('macro_f1', 0)):.3f} vs baseline",
        )
    with col_m3:
        st.metric(
            "Test Examples",
            test_metrics.get("test_size", 0),
        )
    
    if test_metrics.get("practice"):
        st.warning("⚠️ **Practice model results** — English teaching data only. Not indicative of Lingala performance.")
    
    # Per-label F1
    st.subheader("Per-Label F1 Scores")
    report = model_metrics.get("report", {})
    label_order = model_metrics.get("label_order", [])
    
    perf_rows = []
    for label in label_order:
        if label in report and isinstance(report[label], dict):
            perf_rows.append({
                "Intent": FRIENDLY_MEANINGS.get(label, label),
                "Label": label,
                "Precision": f"{report[label].get('precision', 0):.3f}",
                "Recall": f"{report[label].get('recall', 0):.3f}",
                "F1-Score": f"{report[label].get('f1-score', 0):.3f}",
                "Support": int(report[label].get('support', 0)),
            })
    
    if perf_rows:
        perf_df = pd.DataFrame(perf_rows)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
    
    # Confusion matrix
    with st.expander("Confusion Matrix"):
        cm = model_metrics.get("confusion_matrix", [])
        if cm:
            cm_df = pd.DataFrame(
                cm,
                index=[FRIENDLY_MEANINGS.get(l, l) for l in label_order],
                columns=[FRIENDLY_MEANINGS.get(l, l) for l in label_order],
            )
            st.dataframe(cm_df, use_container_width=True)
else:
    st.info("No test metrics available. Run `evaluate.py` after training to generate test results.")

# Dev metrics if available
if dev_metrics_path.exists():
    with open(dev_metrics_path, encoding="utf-8") as f:
        dev_metrics = json.load(f)
    with st.expander("Development Set Metrics (used for model selection)"):
        st.json(dev_metrics)

# ---------------------------------------------------------------------------
# Section 4: Dataset Information
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Dataset Information")

summary_data = summary()

if not summary_data["exists"]:
    st.warning(
        f"No contribution data found at `{summary_data['path']}`. "
        "Run `python ingest_batch.py` first."
    )
else:
    st.write(f"**Language:** {summary_data['language']}")
    st.write(f"**Total accepted records:** {summary_data['total']}")
    
    # Split distribution
    split_dist = summary_data.get("split_distribution", {})
    if split_dist:
        st.subheader("Split Distribution")
        split_df = pd.DataFrame([
            {"Split": k.capitalize(), "Records": v} for k, v in split_dist.items()
        ])
        st.dataframe(split_df, use_container_width=True, hide_index=True)
        
        # Check if splits are properly assigned
        train_count = split_dist.get("train", 0)
        dev_count = split_dist.get("dev", 0)
        test_count = split_dist.get("test", 0)
        unassigned = split_dist.get("", 0)
        
        if unassigned > 0:
            st.warning(
                f"⚠️ **{unassigned} records have no split assigned.** "
                "The model cannot be trained until splits are assigned. "
                "This is a prerequisite for the backend lead (Tatyana) to run "
                "`train.py` and `evaluate.py` on the real Lingala data."
            )
        elif train_count == 0 or dev_count == 0 or test_count == 0:
            st.warning(
                "⚠️ One or more splits are empty. "
                "Minimum required: 15 train, 5 dev, 5 test per label."
            )
        else:
            st.success(
                f"✅ Splits assigned: train={train_count}, dev={dev_count}, test={test_count}. "
                "Ready for training."
            )
    
    # Label distribution
    st.subheader("Label Distribution (target: 25 each)")
    label_progress = summary_data.get("label_progress", [])
    if label_progress:
        label_df = pd.DataFrame([
            {
                "Intent": FRIENDLY_MEANINGS.get(item["label"], item["label"]),
                "Label": item["label"],
                "Achieved": item["achieved"],
                "Target": item["target"],
                "Status": "✅ Reached" if item["reached"] else f"❌ Need {item['target'] - item['achieved']} more",
            }
            for item in label_progress
        ])
        st.dataframe(label_df, use_container_width=True, hide_index=True)
    
    # Volunteer allocation
    st.subheader("Volunteer Allocation (test records)")
    volunteer_progress = summary_data.get("volunteer_progress", [])
    if volunteer_progress:
        vol_df = pd.DataFrame([
            {
                "Volunteer": item["code"],
                "Achieved": item["achieved"],
                "Target": item["target"],
                "Status": "✅ Reached" if item["reached"] else f"❌ Need {item['target'] - item['achieved']} more",
            }
            for item in volunteer_progress
        ])
        st.dataframe(vol_df, use_container_width=True, hide_index=True)
    
    # Review coverage
    st.subheader("Review Coverage")
    review_cov = summary_data.get("review_coverage", {})
    if review_cov:
        rev_df = pd.DataFrame([
            {"Status": k, "Count": v} for k, v in review_cov.items()
        ])
        st.dataframe(rev_df, use_container_width=True, hide_index=True)
    
    # Batch milestones
    st.subheader("Batch Milestones")
    batch_prog = summary_data.get("batch_progress", [])
    if batch_prog:
        batch_df = pd.DataFrame([
            {
                "Milestone": item["name"],
                "Target": item["target"],
                "Achieved": item["achieved"],
                "Status": "✅ Reached" if item["reached"] else "⏳ In Progress",
            }
            for item in batch_prog
        ])
        st.dataframe(batch_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Section 5: Limitations
# ---------------------------------------------------------------------------
st.divider()
st.header("5. Limitations & Disclaimers")

st.markdown("""
### Data Limitations
- **Small dataset**: ~250 Lingala sentences total (25 per intent class)
- **Single dialect**: Data collected from a limited speaker pool
- **No audio**: Text-only classification; no speech recognition component
- **Clean text**: No noise, code-switching, or informal variants in training data

### Model Limitations
- **Character TF-IDF + Logistic Regression**: Simple baseline, no semantic understanding
- **Uncalibrated probabilities**: Model confidence ≠ true correctness probability
- **Closed-set classification**: Always predicts one of 10 known labels, even for out-of-domain input
- **No context**: Each sentence classified independently; no dialogue history

### Evaluation Limitations
- **Practice model only**: Current results are from English teaching fixtures
- **Real Lingala model not yet trained**: Requires split assignment in contribution.csv
- **Test set evaluated once**: No hyperparameter tuning on test data (per datathon rules)
- **No cross-validation**: Single train/dev/test split

### Deployment Limitations
- **Research prototype only**: Not suitable for production use
- **No real actions**: Predictions are simulated routes; no calendar, music, or weather APIs called
- **English practice model**: Current deployed model is trained on English, not Lingala
""")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Team 07 Datalynk • Strathmore NLP Hub Datathon 2026 • "
    "Track A: Intent Classification • Prototype v0.1"
)