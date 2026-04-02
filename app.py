"""QS Subject Rankings Dashboard — Streamlit entry point."""

import streamlit as st
from src.constants import (
    TARGET_UNIVERSITIES,
    UNIVERSITY_SHORT_NAMES,
    FACULTY_AREAS,
)
from src.data_loader import load_qs_data, load_scival_data, get_available_subjects, filter_target_universities
from src.weights import load_weights

st.set_page_config(
    page_title="QS Subject Rankings Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("QS Subject Rankings Dashboard")
st.caption("Comparing São Paulo public universities across areas of knowledge")


# --- Data Loading (cached) ---
@st.cache_data
def cached_load_qs():
    return load_qs_data()


@st.cache_data
def cached_load_scival():
    return load_scival_data()


@st.cache_data
def cached_load_weights():
    return load_weights()


qs_data = cached_load_qs()
scival_data = cached_load_scival()
weights = cached_load_weights()

if qs_data.empty:
    st.error(
        "No QS data found. Place QS Subject Rankings xlsx files in `data/qs/` "
        "and restart the app."
    )
    st.stop()

# Filter to target universities for subject/year discovery
target_data = filter_target_universities(qs_data)

# --- Sidebar ---
st.sidebar.header("Filters")

# University selector
short_to_full = {v: k for k, v in UNIVERSITY_SHORT_NAMES.items()}
available_short = [
    UNIVERSITY_SHORT_NAMES.get(uni, uni)
    for uni in target_data["institution"].unique()
    if uni in UNIVERSITY_SHORT_NAMES
]
selected_short = st.sidebar.multiselect(
    "Universities",
    options=sorted(available_short),
    default=sorted(available_short),
)
selected_universities = [short_to_full.get(s, s) for s in selected_short]

# Faculty area selector
selected_faculty = st.sidebar.selectbox("Faculty Area", FACULTY_AREAS)

# Subject selector (filtered by faculty area and target universities)
# Put broad field at the top as default, then individual subjects
available_subjects = get_available_subjects(target_data, faculty_area=selected_faculty)
broad_label = f"📊 {selected_faculty} (Broad Field)"
individual_subjects = [s for s in available_subjects if s != selected_faculty]
subject_options = [broad_label] + sorted(individual_subjects) if available_subjects else ["(no subjects available)"]
selected_subject_raw = st.sidebar.selectbox("Subject", options=subject_options)
# Map broad label back to actual sheet name
selected_subject = selected_faculty if selected_subject_raw == broad_label else selected_subject_raw
is_broad_field = (selected_subject == selected_faculty)

# Year selector
available_years = sorted(target_data["year"].unique(), reverse=True)
default_year = 2026 if 2026 in available_years else available_years[0] if available_years else 2026
selected_year = st.sidebar.selectbox("Year", options=available_years, index=0)

# Store selections in session state for tab access
st.session_state["selected_universities"] = selected_universities
st.session_state["selected_subject"] = selected_subject
st.session_state["selected_faculty"] = selected_faculty
st.session_state["selected_year"] = selected_year

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Score Decomposition",
    "🎯 Gap Analysis",
    "🔬 Bibliometric Deep Dive",
    "🎛️ Simulator",
    "🏛️ Peer Benchmarking",
])

with tab1:
    from tabs.tab1_decomposition import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab2:
    from tabs.tab2_gap_analysis import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab3:
    from tabs.tab3_deep_dive import render
    render(scival_data, selected_universities, selected_faculty, is_broad_field)

with tab4:
    from tabs.tab4_simulator import render
    render(qs_data, scival_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab5:
    from tabs.tab5_benchmarking import render
    render(qs_data, scival_data, selected_universities, selected_faculty, selected_subject, selected_year)
