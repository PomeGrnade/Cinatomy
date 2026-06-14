"""Main entry point and router for the Cinatomy Streamlit application."""

import streamlit as st
from utils.data_loader import load_data, get_movie_list

st.set_page_config(
    page_title="Cinatomy - Movie Intelligence",
    page_icon=":material/movie:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS globally
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Load data globally into session state
if "data" not in st.session_state:
    with st.spinner("Loading movie database..."):
        st.session_state["data"] = load_data()

df = st.session_state["data"]
movie_list = get_movie_list(df)

# Persistent Search Bar on top
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("<h2 style='margin:0; font-family: var(--font-heading);'><span class='material-symbols-rounded' style='vertical-align: middle;'>movie</span> Cinatomy</h2>", unsafe_allow_html=True)
with col2:
    # Use empty string for default so we don't force a selection
    current_movie = st.session_state.get("selected_movie", "")
    options = [""] + movie_list
    idx = options.index(current_movie) if current_movie in options else 0

    selected = st.selectbox(
        "Search any movie...", 
        options,
        index=idx,
        label_visibility="collapsed"
    )
    if selected and selected != current_movie:
        # User selected a new movie!
        st.session_state["selected_movie"] = selected
        st.session_state["explicit_movie_request"] = True
        st.switch_page("pages/report_card.py")

st.divider()

# Set up navigation
pages = {
    "Navigation": [
        st.Page("pages/home.py", title="Home", icon=":material/home:", default=True),
        st.Page("pages/report_card.py", title="Movie Report Card", icon=":material/analytics:"),
        st.Page("pages/discover.py", title="Discover Movies", icon=":material/search:"),
    ]
}

pg = st.navigation(pages)
pg.run()
