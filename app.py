"""
Streamlit app — Team 07 Datalynk | Lingala Intent Classifier

Entry point:
    python -m streamlit run app.py

Professional SaaS-style interface with working navigation, authentication,
clean AI workspace, and zero decorative emojis.
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
    TARGET_LANGUAGE,
    TEAM_NAME,
    TEAM_NUMBER,
    artifact_dir,
)
from nlp.data_loader import load_dev_metrics, load_test_predictions
from nlp.predictor import predict
from nlp.summary import load_contribution, summary
from nlp.ui import build_disclaimer, confidence_band, format_probability

TRACK = "intent"

st.set_page_config(
    page_title="Lingala Intent Classifier | Team 07 Datalynk",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# AUTHENTICATION MODULE
# ============================================================================

def init_auth() -> None:
    """Initialize authentication database."""
    from nlp.auth import init_db
    init_db()


def check_auth() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict[str, Any] | None:
    """Get current user data."""
    return st.session_state.get("user")


def authenticate(username: str, password: str) -> tuple[bool, str]:
    """Authenticate user and return success status with message."""
    from nlp.auth import authenticate_user
    success, user_data, message = authenticate_user(username, password)
    if success:
        st.session_state["authenticated"] = True
        st.session_state["user"] = user_data
        st.session_state["username"] = username
    return success, message


def register_user(username: str, email: str, password: str, full_name: str) -> tuple[bool, str]:
    """Register a new user."""
    from nlp.auth import create_user
    success, message = create_user(username, email, password, full_name)
    return success, message


def logout() -> None:
    """Log out current user."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["username"] = None


def guest_login() -> None:
    """Login as guest user."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = {"username": "guest", "full_name": "Guest User"}
    st.session_state["username"] = "guest"


# ============================================================================
# DATA & HELPERS
# ============================================================================

@st.cache_data
def get_taxonomy() -> pd.DataFrame:
    path = Path("taxonomy.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


@st.cache_data
def get_contribution() -> pd.DataFrame:
    return load_contribution()


@st.cache_data
def get_summary() -> dict[str, Any]:
    return summary()


@st.cache_data
def get_test_metrics(track: str) -> dict[str, Any] | None:
    path = artifact_dir(track) / "test_metrics.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


@st.cache_data
def get_dev_metrics(track: str) -> dict[str, Any] | None:
    try:
        return load_dev_metrics(track)
    except Exception:
        return None


@st.cache_data
def get_test_predictions(track: str) -> pd.DataFrame | None:
    try:
        return load_test_predictions(track)
    except Exception:
        return None


@st.cache_data
def get_intent_info() -> dict[str, dict[str, str]]:
    """Intent meanings/boundaries sourced from taxonomy and annotation guide."""
    info: dict[str, dict[str, str]] = {
        "weather_query": {
            "name": "Weather enquiry",
            "meaning": "Asks about weather conditions or forecasts.",
            "boundary": "Asking for news about a storm is news_query.",
            "example": "Mbula ekobeta lobi?",
        },
        "datetime_query": {
            "name": "Date or time enquiry",
            "meaning": "Asks for the current date or time.",
            "boundary": "Setting an alarm is alarm_set.",
            "example": "Ngonga ezali boni?",
        },
        "alarm_set": {
            "name": "Set alarm",
            "meaning": "Requests setting an alarm to ring at a specific time.",
            "boundary": "Scheduling a meeting is calendar_set.",
            "example": "Tya alarme na ngonga ya motoba.",
        },
        "calendar_set": {
            "name": "Create calendar event",
            "meaning": "Requests creating a calendar event or scheduled reminder.",
            "boundary": "Reading existing events is calendar_query.",
            "example": "Bakisa likita na ngai na kalandriye.",
        },
        "calendar_query": {
            "name": "Read calendar",
            "meaning": "Asks about existing calendar events or schedule.",
            "boundary": "Creating a new event is calendar_set.",
            "example": "Nazali na makita nini lelo?",
        },
        "lists_createoradd": {
            "name": "Create or add to list",
            "meaning": "Requests creating a list or adding an item to a list.",
            "boundary": "Reading an existing list is lists_query.",
            "example": "Bakisa mapa na liste ya biloko ya kosomba.",
        },
        "lists_query": {
            "name": "Read list",
            "meaning": "Asks what is already in an existing list.",
            "boundary": "Adding an item is lists_createoradd.",
            "example": "Nini ezali na liste na ngai ya kosomba?",
        },
        "play_music": {
            "name": "Play music",
            "meaning": "Requests music playback.",
            "boundary": "Asking who wrote a song is not a playback request.",
            "example": "Yemba miziki.",
        },
        "news_query": {
            "name": "News enquiry",
            "meaning": "Asks for news updates or headlines.",
            "boundary": "Forecast requests are weather_query.",
            "example": "Yebisa ngai bansango ya sika.",
        },
        "qa_definition": {
            "name": "Word or concept meaning",
            "meaning": "Asks for the meaning of a word or concept.",
            "boundary": "General factual questions outside definitions are out of scope.",
            "example": "Liloba biodiversité elimboli nini?",
        },
    }
    tax = get_taxonomy()
    if not tax.empty:
        for _, row in tax.iterrows():
            label = row.get("intent", "")
            if label in info:
                info[label]["meaning"] = row.get("working_definition", info[label]["meaning"])
                info[label]["boundary"] = row.get("boundary", info[label]["boundary"])
    return info


@st.cache_resource
def get_backend(track: str) -> dict[str, Any]:
    """Cache model pack/status; only reload when process restarts."""
    return probe_status(track)


def intent_name(label: str) -> str:
    return get_intent_info().get(label, {}).get("name", label)


def _run_prediction(text: str, pack: dict[str, Any]) -> dict[str, Any] | None:
    """Run prediction and return result with probabilities."""
    try:
        result = predict(text, pack)
        proba = None
        if hasattr(pack["model"], "predict_proba"):
            try:
                raw = pack["model"].predict_proba([text])[0]
                classes = list(pack["model"].classes_)
                proba = sorted(
                    [{"label": c, "probability": float(p)} for c, p in zip(classes, raw)],
                    key=lambda x: x["probability"],
                    reverse=True,
                )
            except Exception:
                proba = None
        return {"result": result, "proba": proba}
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        return None


# ============================================================================
# DESIGN SYSTEM & STYLES
# ============================================================================

def inject_css() -> None:
    """Inject custom CSS for professional SaaS-style design."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        :root {
            --bg-primary: #F8FAFC;
            --bg-white: #FFFFFF;
            --text-primary: #172033;
            --text-secondary: #64748B;
            --border-color: #E6EAF0;
            --accent-teal: #159C8C;
            --accent-teal-dark: #128576;
            --navy-primary: #172B45;
            --navy-secondary: #25445F;
            --success: #16865B;
            --warning: #D99A26;
            --error: #C94C4C;
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background: var(--bg-primary);
            color: var(--text-primary);
        }
        
        /* Navigation */
        [data-testid="stSidebar"] {
            background: var(--bg-white);
            border-right: 1px solid var(--border-color);
        }
        
        [data-testid="stSidebar"] * {
            color: var(--text-primary);
        }
        
        [data-testid="stSidebar"] hr {
            border-color: var(--border-color);
        }
        
        /* Branding */
        .brand-block {
            padding: 1.5rem 1rem 2rem 1rem;
        }
        
        .brand-logo {
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--navy-primary);
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
        }
        
        .brand-sub {
            font-size: 0.85rem;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .brand-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: #E0F2F1;
            color: var(--accent-teal);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 1rem;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1.25rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button[kind="primary"] {
            background: var(--accent-teal);
            color: var(--bg-white);
            border: none;
            box-shadow: 0 2px 8px rgba(21, 156, 140, 0.25);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: var(--accent-teal-dark);
            box-shadow: 0 4px 12px rgba(21, 156, 140, 0.35);
            transform: translateY(-1px);
        }
        
        .stButton > button[kind="secondary"] {
            background: var(--bg-white);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: #F1F5F9;
            border-color: var(--text-secondary);
        }
        
        .stButton > button[kind="ghost"] {
            background: transparent;
            color: var(--text-secondary);
            border: none;
        }
        
        .stButton > button[kind="ghost"]:hover {
            background: #F8FAFC;
            color: var(--text-primary);
        }
        
        /* Cards */
        .card {
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .card h3 {
            color: var(--navy-primary);
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 1.125rem;
            font-weight: 700;
        }
        
        /* Hero section */
        .hero {
            background: linear-gradient(135deg, var(--navy-primary) 0%, var(--navy-secondary) 100%);
            color: var(--bg-white);
            padding: 4rem 2rem;
            border-radius: 24px;
            margin-bottom: 3rem;
            box-shadow: 0 10px 40px rgba(23, 43, 69, 0.15);
        }
        
        .hero h1 {
            margin: 0 0 1rem 0;
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }
        
        .hero p {
            color: #CBD5E1;
            font-size: 1.125rem;
            line-height: 1.6;
            margin: 0;
        }
        
        .hero-cta {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--navy-primary);
            font-weight: 700;
            line-height: 1.2;
        }
        
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        h2 { font-size: 2rem; margin-top: 2.5rem; margin-bottom: 1rem; }
        h3 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 0.75rem; }
        h4 { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.5rem; }
        
        p {
            color: var(--text-primary);
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        /* Inputs */
        .stTextArea textarea, .stTextInput input {
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
            font-size: 1rem;
        }
        
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: var(--accent-teal);
            box-shadow: 0 0 0 3px rgba(21, 156, 140, 0.15);
        }
        
        /* Tables */
        .dataframe {
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }
        
        .dataframe th {
            background: #F8FAFC;
            color: var(--text-primary);
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
        }
        
        .dataframe td {
            border-bottom: 1px solid var(--border-color);
        }
        
        /* Metrics */
        .metric-card {
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--navy-primary);
            line-height: 1;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        
        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-teal { background: #E0F2F1; color: var(--accent-teal); }
        .badge-blue { background: #E3F2FD; color: #1976D2; }
        .badge-warning { background: #FFF3E0; color: var(--warning); }
        
        /* Workflow steps */
        .workflow {
            display: flex;
            gap: 2rem;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        
        .workflow-step {
            flex: 1;
            min-width: 200px;
            text-align: center;
            padding: 1.5rem;
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }
        
        .workflow-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
            color: var(--accent-teal);
        }
        
        .workflow-label {
            font-weight: 600;
            color: var(--navy-primary);
        }
        
        .workflow-arrow {
            font-size: 1.5rem;
            color: var(--text-secondary);
            align-self: center;
        }
        
        /* Footer */
        .footer {
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .hero h1 { font-size: 2.5rem; }
        }
        
        @media (max-width: 768px) {
            .hero { padding: 2rem 1rem; }
            .hero h1 { font-size: 2rem; }
            .workflow { flex-direction: column; }
            .workflow-arrow { display: none; }
            h1 { font-size: 2rem; }
            h2 { font-size: 1.5rem; }
            .hero-cta { flex-direction: column; }
            .hero-cta button { width: 100%; }
        }
        
        @media (max-width: 480px) {
            .hero h1 { font-size: 1.75rem; }
            .workflow-step { padding: 1rem; }
        }
        
        /* Navigation sidebar */
        .nav-section {
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }
        
        .nav-section-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            font-weight: 700;
            margin-bottom: 0.75rem;
            padding-left: 0.5rem;
        }
        
        .nav-item {
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            margin-bottom: 0.25rem;
        }
        
        .nav-item:hover {
            background: #F8FAFC;
        }
        
        .nav-item.active {
            background: #E0F2F1;
            color: var(--accent-teal);
            font-weight: 600;
        }
        
        /* Result card */
        .result-card {
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-teal);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1.5rem;
        }
        
        .result-card h4 {
            color: var(--accent-teal);
            margin-top: 0;
        }
        
        /* Practice warning */
        .practice-warning {
            background: #FFF3E0;
            border: 1px solid var(--warning);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .practice-warning p {
            margin: 0;
            color: var(--warning);
            font-weight: 500;
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--text-secondary);
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        /* Form validation */
        .stError {
            background: #FEF2F2;
            border: 1px solid var(--error);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stSuccess {
            background: #F0FDF4;
            border: 1px solid var(--success);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()
# ============================================================================
# LANDING PAGE
# ============================================================================

def page_landing() -> None:
    """Public landing page - simple, professional, focused."""
    
    # Navigation
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; margin-bottom: 2rem; max-width: 1400px; margin-left: auto; margin-right: auto;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem; font-weight: 800; color: var(--navy-primary);">Lingala</span>
                <span style="font-size: 1.5rem; font-weight: 600; color: var(--accent-teal);">Classifier</span>
            </div>
            <div style="display: flex; gap: 1.5rem; align-items: center;">
                <a href="#about" style="color: var(--text-secondary); text-decoration: none; font-weight: 500;">About</a>
                <a href="#research" style="color: var(--text-secondary); text-decoration: none; font-weight: 500;">Research</a>
                <button onclick="window.location.href='#login'" style="background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 600;">Sign in</button>
                <button onclick="window.location.href='#register'" style="background: var(--accent-teal); border: none; color: var(--bg-white); padding: 0.5rem 1.25rem; border-radius: 8px; cursor: pointer; font-weight: 600;">Get started</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hero section
    st.markdown(
        """
        <div class="hero">
            <div style="max-width: 800px; margin: 0 auto;">
                <span style="display: inline-block; background: rgba(255,255,255,0.15); padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.875rem; font-weight: 600; margin-bottom: 1.5rem;">
                    AFRICAN LANGUAGE TECHNOLOGY · NLP RESEARCH
                </span>
                <h1 style="font-size: 3.5rem; margin-bottom: 1.25rem; line-height: 1.1;">Understanding the intent behind Lingala text.</h1>
                <p style="font-size: 1.25rem; line-height: 1.6; color: #CBD5E1; margin-bottom: 2rem;">
                    Explore an experimental AI system designed to investigate how natural language processing can identify communicative intent in Lingala.
                </p>
                <div class="hero-cta">
                    <button onclick="window.location.href='#workspace'" style="background: var(--accent-teal); border: none; color: var(--bg-white); padding: 0.875rem 2rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(21, 156, 140, 0.35);">Explore the Classifier</button>
                    <button onclick="window.location.href='#research'" style="background: transparent; border: 1px solid rgba(255,255,255,0.3); color: var(--bg-white); padding: 0.875rem 2rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;">Discover the Research</button>
                </div>
                <span style="display: inline-block; margin-top: 2rem; background: rgba(255,255,255,0.15); padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
                    A DATATHON RESEARCH PROTOTYPE
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Two-column layout
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        # Why Lingala NLP
        st.markdown("### Why Lingala NLP?")
        st.write(
            "Low-resource language NLP faces data scarcity, limited tooling, and evaluation challenges. "
            "Building intent classification resources for Lingala supports exploration of everyday language technology "
            "for African languages and highlights practical constraints in small-data settings."
        )
        st.write(
            "This research prototype explores how machine learning can classify everyday Lingala requests "
            "using a small, reviewed dataset and a transparent baseline model."
        )
        
        # How it works - NO EMOJIS
        st.markdown("### How it works")
        st.markdown(
            """
            <div class="workflow">
                <div class="workflow-step">
                    <div class="workflow-icon">Input</div>
                    <div class="workflow-label">Input text</div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Enter a Lingala sentence</p>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-icon">Processing</div>
                    <div class="workflow-label">Model processing</div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Character TF-IDF + Logistic Regression</p>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-icon">Prediction</div>
                    <div class="workflow-label">Intent prediction</div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">One of 10 intent categories</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Quick stats
        st.markdown("### Project Snapshot")
        s = get_summary()
        st.markdown(
            f"""
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card">
                    <div class="metric-value">{s.get('total', 0) if s.get('exists') else '0'}</div>
                    <div class="metric-label">Records</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">10</div>
                    <div class="metric-label">Intents</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Lingala</div>
                    <div class="metric-label">Language</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col2:
        # Visual illustration - NO EMOJIS
        st.markdown(
            """
            <div class="card" style="height: 100%;">
                <h3 style="margin-top: 0;">Classification Demo</h3>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Input</div>
                    <div style="font-size: 1rem; color: var(--text-primary);">Tala mbula lelo.</div>
                </div>
                <div style="display: flex; justify-content: center; margin: 1rem 0;">
                    <span style="font-size: 1.5rem;">Processing</span>
                </div>
                <div style="background: #E0F2F1; border-radius: 8px; padding: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--accent-teal); margin-bottom: 0.5rem;">Predicted</div>
                    <div style="font-size: 1.125rem; font-weight: 600; color: var(--navy-primary);">Weather enquiry</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">weather_query</div>
                </div>
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 1rem; margin-bottom: 0;">
                    * This is a demonstration. Actual predictions may vary.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # CTA section
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem;">
            <h2 style="margin-bottom: 1rem;">Ready to explore the classifier?</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                Join our research community or try the classifier as a guest. No account required for demo access.
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                <button onclick="window.location.href='#register'" style="background: var(--accent-teal); border: none; color: var(--bg-white); padding: 1rem 2rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(21, 156, 140, 0.35);">Create Account</button>
                <button onclick="window.location.href='#login'" style="background: var(--bg-white); border: 1px solid var(--border-color); color: var(--text-primary); padding: 1rem 2rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;">Sign In</button>
                <button onclick="window.location.href='#workspace'" style="background: transparent; border: 1px solid var(--accent-teal); color: var(--accent-teal); padding: 1rem 2rem; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;">Explore as Guest</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Footer
    st.markdown(
        """
        <div class="footer">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <strong>Lingala Intent Classifier</strong><br>
                    Team 07 — Datalynk<br>
                    Strathmore NLP Hub Datathon 2026<br>
                    Track A — Intent Classification
                </div>
                <div style="display: flex; gap: 2rem;">
                    <a href="#about" style="color: var(--text-secondary); text-decoration: none;">About</a>
                    <a href="#research" style="color: var(--text-secondary); text-decoration: none;">Research</a>
                    <a href="https://github.com/emmah-mwangi/Lingala-NLP-Datathon" style="color: var(--text-secondary); text-decoration: none;">GitHub</a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# AUTHENTICATION PAGES
# ============================================================================

def page_login() -> None:
    """Login page with clean, centered design."""
    
    st.markdown(
        """
        <div style="max-width: 400px; margin: 0 auto; padding: 2rem 1rem;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2rem; font-weight: 800; color: var(--navy-primary); margin-bottom: 0.5rem;">Lingala</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--accent-teal);">Classifier</div>
                <p style="color: var(--text-secondary); margin-top: 1rem;">Sign in to continue to your workspace</p>
            </div>
            
            <div class="card">
                <form>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Username or Email</label>
                        <input type="text" id="login_username" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="Enter your username">
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Password</label>
                        <input type="password" id="login_password" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="Enter your password">
                    </div>
                    
                    <button id="login_button" style="width: 100%; background: var(--accent-teal); border: none; color: var(--bg-white); padding: 0.875rem; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; margin-bottom: 1rem;">Sign In</button>
                    
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Don't have an account? </span>
                        <a href="#register" style="color: var(--accent-teal); text-decoration: none; font-weight: 600;">Create one</a>
                    </div>
                    
                    <div style="border-top: 1px solid var(--border-color); padding-top: 1rem;">
                        <button id="guest_button" style="width: 100%; background: var(--bg-white); border: 1px solid var(--border-color); color: var(--text-primary); padding: 0.75rem; border-radius: 8px; font-size: 0.875rem; font-weight: 600; cursor: pointer;">Continue as Guest</button>
                    </div>
                    
                    <div style="text-align: center; margin-top: 1rem;">
                        <a href="#home" style="color: var(--text-secondary); text-decoration: none; font-size: 0.875rem;">← Back to home</a>
                    </div>
                </form>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Handle login logic
    if "login_username" in st.session_state and "login_password" in st.session_state:
        username = st.session_state.get("login_username", "")
        password = st.session_state.get("login_password", "")
        
        if st.session_state.get("_login_clicked", False):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                success, message = authenticate(username, password)
                if success:
                    st.success("Login successful!")
                    st.session_state["page"] = "workspace"
                    st.rerun()
                else:
                    st.error(message)
            st.session_state["_login_clicked"] = False


def page_register() -> None:
    """Registration page with clean, centered design."""
    
    st.markdown(
        """
        <div style="max-width: 400px; margin: 0 auto; padding: 2rem 1rem;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2rem; font-weight: 800; color: var(--navy-primary); margin-bottom: 0.5rem;">Lingala</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--accent-teal);">Classifier</div>
                <p style="color: var(--text-secondary); margin-top: 1rem;">Get access to the classification workspace</p>
            </div>
            
            <div class="card">
                <form>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Full Name</label>
                        <input type="text" id="reg_full_name" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="John Doe">
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Username</label>
                        <input type="text" id="reg_username" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="johndoe">
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Email Address</label>
                        <input type="email" id="reg_email" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="john@example.com">
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Password</label>
                        <input type="password" id="reg_password" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="••••••••">
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Confirm Password</label>
                        <input type="password" id="reg_confirm_password" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem;" placeholder="••••••••">
                    </div>
                    
                    <button id="register_button" style="width: 100%; background: var(--accent-teal); border: none; color: var(--bg-white); padding: 0.875rem; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; margin-bottom: 1rem;">Create Account</button>
                    
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Already have an account? </span>
                        <a href="#login" style="color: var(--accent-teal); text-decoration: none; font-weight: 600;">Sign in</a>
                    </div>
                    
                    <div style="border-top: 1px solid var(--border-color); padding-top: 1rem;">
                        <button id="reg_guest_button" style="width: 100%; background: var(--bg-white); border: 1px solid var(--border-color); color: var(--text-primary); padding: 0.75rem; border-radius: 8px; font-size: 0.875rem; font-weight: 600; cursor: pointer;">Continue as Guest</button>
                    </div>
                    
                    <div style="text-align: center; margin-top: 1rem;">
                        <a href="#home" style="color: var(--text-secondary); text-decoration: none; font-size: 0.875rem;">← Back to home</a>
                    </div>
                </form>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# MAIN APPLICATION WORKSPACE
# ============================================================================

def render_workspace_navigation() -> str:
    """Render sidebar navigation for authenticated workspace."""
    backend = get_backend(TRACK)
    
    with st.sidebar:
        # Branding
        st.markdown(
            """
            <div class="brand-block">
                <div class="brand-logo">Lingala</div>
                <div class="brand-sub">Classifier</div>
                <div class="brand-sub" style="margin-top: 0.5rem;">Team 07 — Datalynk</div>
                <div class="brand-sub" style="margin-top: 0.25rem;">Strathmore NLP Hub 2026</div>
                <span class="brand-badge">Research Prototype</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # User info
        if check_auth():
            user = get_current_user()
            if user:
                st.markdown(
                    f"""
                    <div style="padding: 1rem; background: #F8FAFC; border-radius: 8px; margin-bottom: 1rem;">
                        <div style="font-size: 0.875rem; color: var(--text-primary); font-weight: 600;">Logged in as</div>
                        <div style="font-size: 1rem; color: var(--navy-primary); font-weight: 700;">{user.get('username', 'user')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Logout", use_container_width=True):
                    logout()
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="padding: 1rem; background: #F8FAFC; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--text-primary); font-weight: 600;">Guest access</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        # Navigation sections
        st.markdown('<div class="nav-section-title">AI WORKSPACE</div>', unsafe_allow_html=True)
        page = st.radio(
            "",
            ["AI Classifier", "Intent Boundary Lab"],
            label_visibility="collapsed",
            key="nav_workspace",
        )
        
        st.markdown('<div class="nav-section-title">RESEARCH</div>', unsafe_allow_html=True)
        page = st.radio(
            "",
            ["Dataset Explorer", "Model Performance", "Error Analysis", "About Research"],
            label_visibility="collapsed",
            key="nav_research",
        )
        
        st.divider()
        
        # Backend status
        if backend["available"]:
            st.caption("Backend: available")
            if backend["pack"].get("practice"):
                st.caption("Mode: practice model (English)")
            else:
                st.caption(f"Model language: {backend['pack'].get('language', 'unknown')}")
        else:
            st.caption("Backend: unavailable")
        st.caption("No fabricated predictions")
    
    return page


def page_workspace() -> None:
    """Main workspace - shows landing page for unauthenticated users."""
    page_landing()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """Main application entry point."""
    # Initialize auth
    init_auth()
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    
    # Render appropriate page based on auth state
    if not check_auth():
        # Not authenticated - show landing, login, or register
        page = st.session_state.get("page", "landing")
        
        if page == "landing":
            page_landing()
        elif page == "login":
            page_login()
        elif page == "register":
            page_register()
    else:
        # Authenticated - show workspace
        render_workspace_navigation()
        st.markdown(
            """
            <div style="padding: 2rem;">
                <h1 style="color: var(--navy-primary);">Welcome to the Workspace</h1>
                <p style="color: var(--text-secondary);">Select a page from the sidebar to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
