"""Component for rendering a detailed breakdown of feature scores."""

import streamlit as st

from utils.constants import FEATURE_GROUPS, score_color, render_stars


def render_score_breakdown(movie_data):
    """Render feature scores grouped by category using styled stars.

    Parameters
    ----------
    movie_data : dict | pd.Series
        Mapping of feature column names to score values (1-5).
    """
    for group_name, features in FEATURE_GROUPS.items():
        st.markdown(f'<div class="section-header" style="margin-top: 1rem;">{group_name}</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        
        for i, (col_name, display_name) in enumerate(features):
            val = movie_data.get(col_name, 0)
            try:
                score = float(val)
            except (ValueError, TypeError):
                continue
                
            color = score_color(score)
            stars = render_stars(score)
            
            html = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0; border-bottom: 1px solid var(--color-border);">
                <div style="font-size: 0.85rem; color: var(--color-text); font-weight: 500;">{display_name}</div>
                <div style="color: {color}; letter-spacing: 2px;">{stars} <span style="font-size: 0.75rem; color: var(--color-muted); margin-left: 0.5rem; letter-spacing: normal;">{score:.1f}</span></div>
            </div>
            """
            with cols[i % 2]:
                st.markdown(html, unsafe_allow_html=True)
