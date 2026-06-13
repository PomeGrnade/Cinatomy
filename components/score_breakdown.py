"""Component for rendering a detailed breakdown of feature scores."""

import streamlit as st

from utils.constants import FEATURE_GROUPS, score_color


def render_score_breakdown(movie_data):
    """Render feature scores grouped by category using styled horizontal bars.

    Parameters
    ----------
    movie_data : dict | pd.Series
        Mapping of feature column names to score values (1-5).
    """
    for group_name, features in FEATURE_GROUPS.items():
        st.markdown(f'<div class="section-header">{group_name}</div>', unsafe_allow_html=True)
        
        for col_name, display_name in features:
            val = movie_data.get(col_name, 0)
            try:
                score = float(val)
            except (ValueError, TypeError):
                continue
                
            color = score_color(score)
            percentage = (score / 5.0) * 100
            
            html = f"""
            <div class="feature-bar-container">
                <div class="feature-bar-label">{display_name}</div>
                <div class="feature-bar-track">
                    <div class="feature-bar-fill" style="width: {percentage}%; background-color: {color};"></div>
                </div>
                <div class="feature-bar-value">{score:.1f}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
