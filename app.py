"""Main entry point for the Cinatomy Streamlit application."""

import streamlit as st

from utils.data_loader import load_data

st.set_page_config(
    page_title="Cinatomy - Movie Report Card",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass  # Allow running from different directories during dev

# Sidebar
st.sidebar.title("Cinatomy")
st.sidebar.caption("Movie Intelligence Dashboard")

st.sidebar.markdown("""
Welcome to **Cinatomy**, a comprehensive tool for movie analysis.

Navigate using the pages above:
- **Report Card**: Deep dive into individual movies
- **Discover**: Find movies by tuning feature sliders
""")

# Load data globally into session state to prevent re-loading on page change
if "data" not in st.session_state:
    with st.spinner("Loading movie database..."):
        st.session_state["data"] = load_data()

st.title("Welcome to Cinatomy")
st.markdown("""
<div class="report-card">
    <div class="section-header">Start Your Analysis</div>
    <p>Please select a page from the sidebar to begin.</p>
    <ul>
        <li><strong>Report Card:</strong> View detailed spider charts, score breakdowns, and similar movies for a specific title.</li>
        <li><strong>Discover:</strong> Search the database by setting precise ranges for 21 different movie features.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Add a button to jump straight to the report card
if st.button("Open Report Card", type="primary"):
    st.switch_page("pages/1_Report_Card.py")
