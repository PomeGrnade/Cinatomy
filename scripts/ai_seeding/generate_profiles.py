"""
Cinatomy — Movie Experiential Profile Generator
================================================

This script generates the "experiential profile" data for the Cinatomy
dataset. For each movie title in an input CSV, it prompts Gemini 2.5 Flash
to act as a film critic and return a structured, schema-enforced rating
across ~20 experiential dimensions (pacing, emotional payoff, sensory
qualities, plot mechanics, etc.).

REQUIREMENTS
------------
    pip install pandas pydantic google-genai

ENVIRONMENT
-----------
    Requires a Gemini API key set as an environment variable:
        export GEMINI_API_KEY="your_api_key_here"

INPUT FORMAT
------------
    A CSV file with at least one column containing movie titles. If a
    column named "Movie Title" exists it will be used; otherwise the
    first column is used. Any additional columns (e.g. release year)
    are passed to the model as extra context.

OUTPUT FORMAT
-------------
    A CSV file where each row is one movie's flattened profile card.
    Results are appended incrementally, so the script can be safely
    interrupted and re-run — it will skip movies already present in
    the output file (matched on the "movie_title" column).

NOTES ON RELIABILITY
---------------------
    - On HTTP 429 (rate limit) errors, the script waits 20 seconds and
      retries. If it hits 429 twice in a row, it assumes the daily
      free-tier quota is exhausted, saves progress, and exits cleanly
      (exit code 0) so it can be re-run later (e.g. with a different
      API key, or the next day).
    - A 10-second pause between requests keeps the rolling
      tokens-per-minute (TPM) usage within free-tier limits.
"""

import os
import time
import sys
import pandas as pd
from typing import Literal, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ---------------------------------------------------------
# 1. STRUCTURED REPORT CARD SCHEMA
#    (Field descriptions are deliberately omitted to reduce token usage
#    per request; scoring guidance is instead provided in the prompt.)
# ---------------------------------------------------------
class EndFeelingSchema(BaseModel):
    emotional_adjective: Literal["happy", "sad", "disappointed", "bittersweet", "energized", "neutral"]
    ending_rating: int = Field(ge=1, le=5)
    structural_adjective: Literal["rushed", "satisfying", "earned", "ambiguous", "abrupt"]

class SoundSchema(BaseModel):
    audio_balance_issue: bool
    bgm_quality: int = Field(ge=1, le=5)
    song_tracks_quality: int = Field(ge=1, le=5)

class PlotQualitySchema(BaseModel):
    rating: int = Field(ge=1, le=5)
    reasons_for_liking: List[Literal["unpredictable", "plot_twists", "strong_pacing", "tight_structure"]]
    reasons_for_disliking: List[Literal["plot_holes", "predictable", "cliche", "narrative_inconsistency"]]

class MovieProfileCard(BaseModel):
    pacing_efficiency: int = Field(ge=1, le=5)
    originality: int = Field(ge=1, le=5)
    family_friendly: int = Field(ge=1, le=5)
    plot_quality: PlotQualitySchema
    dialogues: int = Field(ge=1, le=5)
    end_feeling: EndFeelingSchema
    immersive: int = Field(ge=1, le=5)
    impactful: int = Field(ge=1, le=5)
    overall_feeling: int = Field(ge=1, le=5)
    visuals: int = Field(ge=1, le=5)
    visual_effects: int = Field(ge=1, le=5)
    sound: SoundSchema
    performance_of_actors: int = Field(ge=1, le=5)
    connected: int = Field(ge=1, le=5)
    references_contained: int = Field(ge=1, le=5)
    cognitive_requirement: int = Field(ge=1, le=5)
    technical_knowledge_required: int = Field(ge=1, le=5)
    photosensitivity_warnings: int = Field(ge=1, le=5)
    animal_harm: int = Field(ge=1, le=5)
    trailer_or_spoiler: int = Field(ge=1, le=5)


# ---------------------------------------------------------
# 2. GENERATION PIPELINE
# ---------------------------------------------------------
def run_profiler(input_csv_path: str, output_csv_path: str):
    client = genai.Client()
    df = pd.read_csv(input_csv_path)
    title_col = 'Movie Title' if 'Movie Title' in df.columns else df.columns[0]

    # Resume from existing progress if the output file already exists
    if os.path.exists(output_csv_path):
        try:
            completed_df = pd.read_csv(output_csv_path)
            processed_titles = set(completed_df['movie_title'].dropna().tolist())
            print(f"📦 Found existing progress. {len(processed_titles)} movies already processed. Resuming...")
        except Exception:
            processed_titles = set()
    else:
        processed_titles = set()

    print(f"🚀 Starting automation loop for {len(df)} movies...")

    for index, row in df.iterrows():
        movie_title = row[title_col]

        # Skip movies already present in the output file
        if movie_title in processed_titles:
            continue

        extra_context = f"Year/Context: {row.to_dict()}" if len(df.columns) > 1 else ""
        print(f"🎬 Evaluating [{index+1}/{len(df)}]: {movie_title}...")

        # Scoring guidance is embedded directly in the prompt (rather than
        # in the schema field descriptions) to keep per-request token usage low
        # while still anchoring the model to a consistent rating scale.
        prompt = f"""
        You are an expert, highly analytical, and unforgiving film critic. 
        Analyze the following movie and extract its profile card details based on your comprehensive historical data of critical consensus, script execution, and audience reception.

        Movie to analyze: {movie_title}
        Context metadata: {extra_context}

        CRITICAL DIRECTION: Do not be overly generous. Use the full 1 to 5 scale dynamically. 
        An average movie should score 3s, not 4s or 5s.

        SCORING FRAMEWORK REFERENCE:
        - pacing_efficiency: 1=Dragged, 3=Deliberate/Slow-burn, 5=Perfectly fast/thrilling.
        - family_friendly: 1=Highly inappropriate, 3=Safe but boring for kids, 5=Universally engaging for family.
        - dialogues: 1=Stilted/Exposition-heavy, 5=Sharp and authentic.
        - immersive: 1=Disconnecting, 5=Hypnotic environment.
        - impactful: 1=Instantly forgettable, 5=Leaves massive footprint.
        """

        attempts = 0
        while attempts < 5:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MovieProfileCard,
                        temperature=0.2
                    ),
                )

                movie_profile: MovieProfileCard = response.parsed

                # Flatten nested schema objects into flat column names
                movie_data = {"movie_title": movie_title}
                for field_name, value in movie_profile.model_dump().items():
                    if isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            movie_data[f"{field_name}_{sub_key}"] = str(sub_val)
                    else:
                        movie_data[field_name] = value

                single_row_df = pd.DataFrame([movie_data])

                # Append incrementally so progress is never lost
                if not os.path.exists(output_csv_path):
                    single_row_df.to_csv(output_csv_path, index=False)
                else:
                    single_row_df.to_csv(output_csv_path, mode='a', header=False, index=False)

                break  # success — move to the next movie

            except APIError as api_err:
                if api_err.code == 429:
                    attempts += 1
                    # If 429 hits twice in a row, treat the daily quota as
                    # exhausted: save progress and exit cleanly so the
                    # script can be re-run later.
                    if attempts >= 2:
                        print("🛑 Daily free-tier token/request quota fully exhausted. Saving progress and exiting. Run script again tomorrow!")
                        sys.exit(0)

                    print(f"⏳ Rate limit hit (429). Waiting 20 seconds to retry (Attempt {attempts}/5)...")
                    time.sleep(20)
                else:
                    print(f"⚠️ API Error for {movie_title}: {api_err}")
                    break
            except Exception as e:
                print(f"⚠️ Error processing {movie_title}: {e}")
                break

        # Pause between requests to stay within free-tier TPM limits
        time.sleep(10.0)

    print(f"\n🎉 Profiling Complete! Seed library verified at: '{output_csv_path}'")


if __name__ == "__main__":
    run_profiler("input_movies.csv", "movie_profiles_database.csv")
