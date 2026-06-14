"""Home page content."""

import random
import streamlit as st

from utils.data_loader import load_data, get_movie_list

# Inject custom CSS
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

st.session_state["last_page"] = "home"

# --- Hero Section ---
st.markdown("""
<div style="text-align: center; padding: 4rem 1rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, var(--color-primary), var(--color-accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Cinatomy</h1>
    <p style="font-size: 1.25rem; color: var(--color-muted); max-width: 600px; margin: 0 auto 2rem auto;">
        Decode the DNA of your favorite films. Explore detailed emotional profiles, plot structures, and discover new movies based on precise feature tuning.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Action Cards ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("""
    <div class="report-card" style="text-align: center; height: 100%;">
        <div style="margin-bottom: 1rem;"><span class="material-symbols-rounded" style="font-size: 3rem; color: var(--color-primary);">analytics</span></div>
        <h3 style="margin-bottom: 0.5rem;">Report Card</h3>
        <p style="color: var(--color-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Deep dive into an individual movie's emotional and structural profile.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Report Card", use_container_width=True, key="btn_rc"):
        st.switch_page("pages/report_card.py")

with col2:
    st.markdown("""
    <div class="report-card" style="text-align: center; height: 100%;">
        <div style="margin-bottom: 1rem;"><span class="material-symbols-rounded" style="font-size: 3rem; color: var(--color-primary);">search</span></div>
        <h3 style="margin-bottom: 0.5rem;">Discover</h3>
        <p style="color: var(--color-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Find your next watch by tuning 21 different movie features.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Discovering", use_container_width=True, key="btn_disc"):
        st.switch_page("pages/discover.py")

with col3:
    st.markdown("""
    <div class="report-card" style="text-align: center; height: 100%;">
        <div style="margin-bottom: 1rem;"><span class="material-symbols-rounded" style="font-size: 3rem; color: var(--color-accent);">casino</span></div>
        <h3 style="margin-bottom: 0.5rem;">Surprise Me</h3>
        <p style="color: var(--color-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Don't know what to look at? Pick a completely random movie.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Pick Random Movie", use_container_width=True, key="btn_rand", type="primary"):
        st.session_state["selected_movie"] = random.choice(movie_list)
        st.session_state["explicit_movie_request"] = True
        st.switch_page("pages/report_card.py")
