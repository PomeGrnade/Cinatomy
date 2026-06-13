"""Discover page for searching movies by feature ranges."""

import streamlit as st

from utils.constants import FEATURE_GROUPS, QUICK_PRESETS, score_color
from utils.data_loader import load_data
from utils.feature_engine import filter_movies

# Ensure CSS is loaded
with open("styles/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Discover Movies")
st.markdown("Find your next watch by tuning movie features.", unsafe_allow_html=True)

df = load_data()

# --- Quick Presets ---
st.markdown('<div class="report-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Quick Presets</div>', unsafe_allow_html=True)

# Use session state to store current slider values so presets can override them
if "filters" not in st.session_state:
    st.session_state["filters"] = {}

preset_cols = st.columns(len(QUICK_PRESETS) + 1)
for i, (preset_name, preset_rules) in enumerate(QUICK_PRESETS.items()):
    with preset_cols[i]:
        if st.button(preset_name, key=f"preset_{preset_name}", use_container_width=True):
            # Apply preset to session state
            for feature_key, val_range in preset_rules.items():
                st.session_state[f"slider_{feature_key}"] = val_range

with preset_cols[-1]:
    if st.button("Reset All", key="preset_reset", use_container_width=True):
        st.session_state.pop("filters", None)
        # Clear all slider states
        for key in list(st.session_state.keys()):
            if key.startswith("slider_"):
                del st.session_state[key]
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- Feature Sliders (Tabbed) ---
st.markdown('<div class="report-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Tune Features</div>', unsafe_allow_html=True)

tabs = st.tabs(list(FEATURE_GROUPS.keys()))

active_filters = []

for i, (group_name, features) in enumerate(FEATURE_GROUPS.items()):
    with tabs[i]:
        for col_name, display_name in features:
            # Get default from session state or use (1, 5)
            default_val = st.session_state.get(f"slider_{col_name}", (1, 5))
            
            # The slider automatically updates session_state if we use key
            val = st.slider(
                display_name,
                min_value=1,
                max_value=5,
                value=default_val,
                key=f"slider_{col_name}",
            )
            
            # Add to active filters if not the full range
            if val != (1, 5):
                active_filters.append((col_name, val[0], val[1]))

st.markdown('</div>', unsafe_allow_html=True)

# --- Results ---
if active_filters:
    st.markdown(f"**Active Filters:** {len(active_filters)}")
    results_df = filter_movies(df, active_filters)
else:
    # If no filters, show top rated by overall feeling
    results_df = df.sort_values("overall_feeling", ascending=False).head(50)
    st.markdown("**Showing Top 50 Movies (No filters applied)**")

st.markdown('<div class="report-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-header">Results ({len(results_df)} movies match)</div>', unsafe_allow_html=True)

if results_df.empty:
    st.info("No movies match the selected criteria. Try broadening your search.")
else:
    # Display in a grid
    grid_cols = 4
    cols = st.columns(grid_cols)
    
    for i, (_, movie) in enumerate(results_df.head(24).iterrows()):  # Limit to 24 for performance
        with cols[i % grid_cols]:
            title = movie["movie_title"]
            poster = movie.get("Poster_Link", "")
            overall = movie.get("overall_feeling", 0)
            color = score_color(overall)
            
            img_html = f'<img src="{poster}" style="width: 100%; border-radius: 8px; margin-bottom: 0.5rem; aspect-ratio: 2/3; object-fit: cover;" onerror="this.src=\'https://via.placeholder.com/300x450?text=No+Poster\'">'
            
            html = f"""
            <div class="movie-card">
                {img_html}
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; font-size: 0.95rem; line-height: 1.2; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;" title="{title}">{title}</h4>
                </div>
                <div style="font-size: 0.8rem; font-weight: 600; color: {color};">★ {overall:.1f} / 5.0</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            if st.button(f"Report", key=f"res_btn_{title}_{i}", use_container_width=True):
                st.session_state["selected_movie"] = title
                st.switch_page("pages/1_Report_Card.py")

st.markdown('</div>', unsafe_allow_html=True)
