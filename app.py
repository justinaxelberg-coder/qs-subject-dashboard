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

col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("assets/metricas_logo.png", width=220)
with col_title:
    st.title("QS Subject Rankings — Dashboard")
    st.caption("Comparando universidades públicas paulistas por área do conhecimento")


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

# --- Barra lateral ---
st.sidebar.header("Filtros")

# Seletor de universidades
short_to_full = {v: k for k, v in UNIVERSITY_SHORT_NAMES.items()}
available_short = [
    UNIVERSITY_SHORT_NAMES.get(uni, uni)
    for uni in target_data["institution"].unique()
    if uni in UNIVERSITY_SHORT_NAMES
]
selected_short = st.sidebar.multiselect(
    "Universidades",
    options=sorted(available_short),
    default=sorted(available_short),
)
selected_universities = [short_to_full.get(s, s) for s in selected_short]

# Seletor de grande área
selected_faculty = st.sidebar.selectbox("Grande Área", FACULTY_AREAS)

# Seletor de disciplina (filtrado por grande área e universidades alvo)
available_subjects = get_available_subjects(target_data, faculty_area=selected_faculty)
broad_label = f"📊 {selected_faculty} (Campo Amplo)"
individual_subjects = [s for s in available_subjects if s != selected_faculty]
subject_options = [broad_label] + sorted(individual_subjects) if available_subjects else ["(nenhuma disciplina disponível)"]
selected_subject_raw = st.sidebar.selectbox("Disciplina", options=subject_options)
# Mapeia o rótulo amplo de volta ao nome da planilha
selected_subject = selected_faculty if selected_subject_raw == broad_label else selected_subject_raw
is_broad_field = (selected_subject == selected_faculty)

# Seletor de ano
available_years = sorted(target_data["year"].unique(), reverse=True)
default_year = 2026 if 2026 in available_years else available_years[0] if available_years else 2026
selected_year = st.sidebar.selectbox("Ano", options=available_years, index=0)

# Store selections in session state for tab access
st.session_state["selected_universities"] = selected_universities
st.session_state["selected_subject"] = selected_subject
st.session_state["selected_faculty"] = selected_faculty
st.session_state["selected_year"] = selected_year

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Decomposição do Escore",
    "🎯 Análise de Lacunas",
    "🔬 Análise Bibliométrica",
    "🎛️ Simulador",
    "🏛️ Benchmarking com Pares",
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
