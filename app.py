"""Main entry point and router for the Cinatomy Streamlit application."""

import streamlit as st

st.set_page_config(
    page_title="Cinatomy - Movie Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up navigation
pages = {
    "Navigation": [
        st.Page("pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/report_card.py", title="Movie Report Card", icon="📊"),
        st.Page("pages/discover.py", title="Discover Movies", icon="🔍"),
    ]
}

pg = st.navigation(pages)
pg.run()
