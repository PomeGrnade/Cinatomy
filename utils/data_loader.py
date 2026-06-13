"""Data loading utilities for the Cinatomy application.

Loads movie profiles, IMDB metadata, and overview datasets, then merges them.
"""

import os

import pandas as pd
import streamlit as st


def _data_path(filename):
    """Return the absolute path to a data file relative to the project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "data", filename)


@st.cache_data
def load_data():
    """Load and merge movie profiles with IMDB metadata.

    Returns a single DataFrame with all profile features, IMDB metadata
    (poster, genre, director, cast, year, runtime, overview), and overviews.
    """
    profiles = pd.read_csv(_data_path("cinatomy_movie_profiles.csv"))
    imdb = pd.read_csv(_data_path("imdb_top_1000.csv"))

    merged = profiles.merge(
        imdb,
        left_on="movie_title",
        right_on="Series_Title",
        how="left",
    )
    
    # Fix blurry IMDB posters by requesting higher resolution (500px width instead of 67px)
    if "Poster_Link" in merged.columns:
        merged["Poster_Link"] = merged["Poster_Link"].str.replace(
            r"\._V1_.*\.jpg$", "._V1_FMjpg_UX500_.jpg", regex=True
        )
        
    return merged


def get_movie_list(df):
    """Return a sorted list of unique movie titles."""
    return sorted(df["movie_title"].unique().tolist())
