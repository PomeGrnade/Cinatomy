"""Component for displaying similar movies."""

import streamlit as st


def render_similar_movies(similar_list, full_df):
    """Display 3 similar movies as clickable cards.

    Parameters
    ----------
    similar_list : list[tuple[str, float]]
        List of ``(title, similarity_score)`` pairs.
    full_df : pd.DataFrame
        Full merged dataframe for poster and metadata lookup.
    """
    if not similar_list:
        st.write("No similar movies found.")
        return

    cols = st.columns(len(similar_list))
    
    for i, (title, sim) in enumerate(similar_list):
        with cols[i]:
            # Find movie data
            movie_rows = full_df[full_df["movie_title"] == title]
            if movie_rows.empty:
                continue
            movie = movie_rows.iloc[0]
            
            poster = movie.get("Poster_Link", "")
            genre = movie.get("Genre", "Unknown")
            year = movie.get("Released_Year", "")
            
            # Use a placeholder if no poster
            img_html = f'<img src="{poster}" style="width: 100%; border-radius: 8px; margin-bottom: 0.5rem; aspect-ratio: 2/3; object-fit: cover;" onerror="this.src=\'https://via.placeholder.com/300x450?text=No+Poster\'">'
            
            html = f"""
            <div class="movie-card">
                {img_html}
                <div class="similarity-badge" style="margin-bottom: 0.5rem;">{sim:.0%} Match</div>
                <h4 style="margin: 0 0 0.25rem 0; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{title}">{title}</h4>
                <div style="font-size: 0.8rem; color: var(--color-muted);">{year} • {genre}</div>
            </div>
            """
            
            st.markdown(html, unsafe_allow_html=True)
            
            # Add a button that sets the session state to navigate to this movie
            if st.button(f"View {title}", key=f"sim_btn_{i}_{title}", use_container_width=True):
                st.session_state["selected_movie"] = title
                st.session_state["explicit_movie_request"] = True
                
                # Check if we are already on the report card page
                if st.session_state.get("last_page") == "report_card":
                    st.rerun()
                else:
                    st.switch_page("pages/report_card.py")
