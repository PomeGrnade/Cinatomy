"""Report Card page for the Cinatomy application."""

import pandas as pd
import random
import streamlit as st

from components.score_breakdown import render_score_breakdown
from components.similar_movies import render_similar_movies
from components.spider_chart import render_spider_chart
from utils.constants import ALL_NUMERIC_FEATURES, SPIDER_FEATURES
from utils.data_loader import get_movie_list, load_data
from utils.feature_engine import find_similar_movies

# Need to ensure CSS is loaded if running independently (though app.py will load it)
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

df = load_data()
movie_list = get_movie_list(df)

# Handle true random selection from navbar navigation
current_page = "report_card"
last_page = st.session_state.get("last_page", "")

if last_page != current_page:
    # We just navigated to this page
    if not st.session_state.get("explicit_movie_request", False):
        # Navigated from the navbar (not explicitly from a movie button)
        st.session_state["selected_movie"] = random.choice(movie_list)
    else:
        # Reset the flag so future navbar clicks randomize again
        st.session_state["explicit_movie_request"] = False

st.session_state["last_page"] = current_page

# Sidebar movie selector
selected_movie = st.sidebar.selectbox(
    "Select a Movie",
    movie_list,
    index=movie_list.index(st.session_state.get("selected_movie", movie_list[0]))
    if st.session_state.get("selected_movie") in movie_list else 0,
    key="report_card_selectbox"
)

# Update session state with selected movie
st.session_state["selected_movie"] = selected_movie

# Get movie data
movie = df[df["movie_title"] == selected_movie].iloc[0]

# Extract metadata
title = movie["movie_title"]
genre = movie.get("Genre", "Unknown")
year = movie.get("Released_Year", "Unknown")
runtime = movie.get("Runtime", "Unknown")
director = movie.get("Director", "Unknown")
poster = movie.get("Poster_Link", "")
overview = movie.get("Overview", "No synopsis available.")
overall_score = float(movie.get("overall_feeling", 0))

# --- Header ---
st.title(title)
st.markdown(f"<div style='color: var(--color-muted); font-size: 1.1rem; margin-bottom: 2rem;'>{genre} • {year} • {runtime} • {director}</div>", unsafe_allow_html=True)

# --- Top Row: Poster & Spider Chart ---
col1, col2 = st.columns([1, 2])

with col1:
    if poster:
        st.markdown(f'<img src="{poster}" style="width: 100%; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); aspect-ratio: 2/3; object-fit: cover;">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width: 100%; aspect-ratio: 2/3; background: var(--color-border); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--color-muted);">No Poster</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">Feature Profile</div>', unsafe_allow_html=True)
    render_spider_chart(movie, SPIDER_FEATURES)

# --- Synopsis Box ---
st.markdown(f'<div class="synopsis-box"><strong>Synopsis:</strong> {overview}</div>', unsafe_allow_html=True)

# --- Overall Score Badge ---
st.markdown(f"""
<div class="overall-score">
    <div class="score-number">{overall_score:.1f} / 5.0</div>
    <div class="score-label">Overall Feeling</div>
</div>
""", unsafe_allow_html=True)

# --- Detailed Feature Breakdown ---
st.markdown('<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)
render_score_breakdown(movie)

# --- Emotional Profile ---
st.markdown('<div class="section-header">Emotional Profile</div>', unsafe_allow_html=True)

emo_col1, emo_col2 = st.columns(2)
with emo_col1:
    st.markdown("**Ending Emotion**")
    if pd.notna(movie.get("end_feeling_emotional_adjective")):
        st.markdown(f'<span class="tag">{movie["end_feeling_emotional_adjective"]}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color: var(--color-muted);">Not recorded</span>', unsafe_allow_html=True)

with emo_col2:
    st.markdown("**Ending Structure**")
    if pd.notna(movie.get("end_feeling_structural_adjective")):
        st.markdown(f'<span class="tag">{movie["end_feeling_structural_adjective"]}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color: var(--color-muted);">Not recorded</span>', unsafe_allow_html=True)

st.markdown("<br>**Plot Strengths**", unsafe_allow_html=True)
strengths = str(movie.get("plot_quality_reasons_for_liking", ""))
if strengths and strengths != "nan":
    for s in strengths.split(','):
        if s.strip():
            st.markdown(f'<span class="tag">{s.strip()}</span>', unsafe_allow_html=True)

st.markdown("<br>**Plot Concerns**", unsafe_allow_html=True)
concerns = str(movie.get("plot_quality_reasons_for_disliking", ""))
if concerns and concerns != "nan":
    for c in concerns.split(','):
        if c.strip():
            st.markdown(f'<span class="tag" style="background: rgba(195, 91, 72, 0.1); border-color: rgba(195, 91, 72, 0.2); color: var(--color-danger);">{c.strip()}</span>', unsafe_allow_html=True)

# --- Similar Movies ---
st.markdown('<div class="section-header">Similar Movies</div>', unsafe_allow_html=True)

# Get all numeric features to compute similarity
numeric_features = [f[0] for f in ALL_NUMERIC_FEATURES]
similar = find_similar_movies(df, selected_movie, numeric_features, top_n=3)

render_similar_movies(similar, df)
