"""Feature engine for normalization, similarity search, and movie filtering."""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine


def normalize_features(df, features):
    """Min-max normalize feature columns to the 0-1 range.

    Parameters
    ----------
    df : pd.DataFrame
        The full movie dataframe.
    features : list[str]
        Column names to normalize.

    Returns
    -------
    pd.DataFrame
        A copy with only the requested columns, each scaled to [0, 1].
    """
    result = df[features].copy()
    for col in features:
        min_val = result[col].min()
        max_val = result[col].max()
        if max_val > min_val:
            result[col] = (result[col] - min_val) / (max_val - min_val)
        else:
            result[col] = 0.5
    return result


def find_similar_movies(df, movie_title, features, top_n=3):
    """Return the *top_n* most similar movies by cosine similarity.

    Parameters
    ----------
    df : pd.DataFrame
        The full movie dataframe.
    movie_title : str
        Title of the reference movie.
    features : list[str]
        Column names to use for the similarity vector.
    top_n : int
        Number of similar movies to return.

    Returns
    -------
    list[tuple[str, float]]
        List of ``(title, similarity_score)`` pairs, sorted descending.
    """
    numeric_df = df[features].apply(pd.to_numeric, errors="coerce").fillna(0)
    normalized = normalize_features(
        numeric_df.assign(movie_title=df["movie_title"]),
        features,
    )

    idx = df[df["movie_title"] == movie_title].index[0]
    target = normalized.loc[idx].values.astype(float)

    similarities = []
    for i, row in normalized.iterrows():
        if i != idx:
            row_vals = row.values.astype(float)
            # Guard against zero vectors
            if np.any(target) and np.any(row_vals):
                sim = 1 - cosine(target, row_vals)
            else:
                sim = 0.0
            similarities.append((df.loc[i, "movie_title"], sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]


def filter_movies(df, filters):
    """Filter movies by feature range sliders.

    Parameters
    ----------
    df : pd.DataFrame
        The full movie dataframe.
    filters : list[tuple[str, int, int]]
        Each entry is ``(feature_column, min_val, max_val)``.

    Returns
    -------
    pd.DataFrame
        Filtered dataframe sorted by ``overall_feeling`` descending.
    """
    mask = pd.Series(True, index=df.index)
    for feature, min_val, max_val in filters:
        mask &= (df[feature] >= min_val) & (df[feature] <= max_val)
    return df[mask].sort_values("overall_feeling", ascending=False)
