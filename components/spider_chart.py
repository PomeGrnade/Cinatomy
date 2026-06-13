"""Plotly radar (spider) chart component for movie feature visualization."""

import plotly.graph_objects as go
import streamlit as st


def render_spider_chart(movie_data, features=None):
    """Render an 8-axis radar chart for a movie and display it in Streamlit.

    Parameters
    ----------
    movie_data : dict | pd.Series
        Mapping of feature column names to score values (1-5).
    features : list[tuple[str, str]] | None
        List of ``(column_name, display_name)`` tuples. If *None*, uses the
        default ``SPIDER_FEATURES`` from constants.
    """
    if features is None:
        from utils.constants import SPIDER_FEATURES
        features = SPIDER_FEATURES

    categories = [f[1] for f in features]
    values = [float(movie_data.get(f[0], 0)) for f in features]

    # Close the polygon by repeating the first point
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.15)",
            line=dict(color="#3B82F6", width=2.5),
            marker=dict(size=7, color="#3B82F6"),
            hovertemplate="%{theta}: %{r}/5<extra></extra>",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=["1", "2", "3", "4", "5"],
                gridcolor="#1E293B",
                linecolor="#1E293B",
                tickfont=dict(size=10, color="#94A3B8"),
            ),
            angularaxis=dict(
                gridcolor="#1E293B",
                linecolor="#1E293B",
                tickfont=dict(size=12, color="#F8FAFC", family="Poppins"),
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC", family="Poppins"),
        margin=dict(l=80, r=80, t=40, b=40),
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
