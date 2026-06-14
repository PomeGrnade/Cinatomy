<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=3000&pause=1000&color=00D2FF&center=true&vCenter=true&width=700&lines=🎬+Cinatomy;Mapping+the+Experiential+DNA+of+Cinema">
  <img alt="Cinatomy" src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=3000&pause=1000&color=7B2FF7&center=true&vCenter=true&width=700&lines=🎬+Cinatomy;Mapping+the+Experiential+DNA+of+Cinema">
</picture>

<p align="center">
  <a href="https://github.com/YOUR_USERNAME/cinatomy/stargazers"><img src="https://img.shields.io/github/stars/YOUR_USERNAME/cinatomy?style=for-the-badge&color=00d2ff" /></a>
  <a href="https://www.kaggle.com/datasets/YOUR_USERNAME/cinatomy-movie-profiles"><img src="https://img.shields.io/badge/Kaggle-Dataset-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white" /></a>
  <a href="https://YOUR_STREAMLIT_APP_URL"><img src="https://img.shields.io/badge/Live_App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" /></a>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Movies-1%2C000-7b2ff7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Dimensions-20%2B-ff6b6b?style=for-the-badge" />
</p>

<p align="center">
  <i>Most movie metadata tells you <b>who made a film.</b><br>
  Cinatomy tells you <b>what it feels like to watch one.</b></i>
</p>

---

## 🚫 The Problem With Movie Ratings

Every major platform gives you the same handful of facts: cast, director, runtime, and one aggregate score that mashes critic opinion, marketing, and audience reaction into a single flat number.

But that's not the question people are actually asking when they sit down to watch something.

The real question is:

> *"Is this the right movie for how I want to feel **right now**?"*

Fast-paced or slow-burn? An ending that lands clean, or one that lingers uncomfortably? Heavy on dialogue, or carried by visuals? Cognitively demanding or easy to switch off to? None of the major platforms expose data at that level — so people fall back on spoiler-heavy forum threads and gut instinct.

**Cinatomy is a structured answer to that question.**

---

## 💡 What It Is

A dataset of **1,000 IMDb top-rated films**, each rated across **25+ experiential dimensions** using Gemini 2.5 Flash as a structured evaluator — not a single "good/bad" score, but a multi-axis profile card:

| Dimension | What it captures |
|---|---|
| `pacing_efficiency` | Does this drag or fly? (1 = sluggish, 5 = thrilling) |
| `cognitive_requirement` | Passive watch or active puzzle? |
| `immersive` | Does the world pull you in? |
| `impactful` | Will you think about this tomorrow? |
| `end_feeling_emotional_adjective` | happy / sad / bittersweet / energized / neutral / disappointed |
| `end_feeling_structural_adjective` | earned / satisfying / ambiguous / rushed / abrupt |
| `connected` | Do you care about the characters? |
| `family_friendly` | Actually watchable with kids? |
| `animal_harm` | Content warning dimension |
| `photosensitivity_warnings` | Accessibility dimension |
| ...and 15 more | See `data_dictionary.csv` for the full schema |

---

## 🔍 What You Can Do With It

### 1. Vibe-Based Recommendations
Instead of "what's a good thriller?", ask "what's a thriller that's fast-paced, easy to follow, and leaves you feeling energized at the end?" — the dimensions make this filterable.

### 2. Decode the `overall_feeling` Formula
The notebook models `overall_feeling` as a function of all other dimensions using feature importance analysis. Spoiler: `impactful` and `connected` carry the most weight — which tracks with how most people describe their favorite films.

### 3. Experiential Clustering
K-Means on the numeric dimensions groups films by *how they feel*, not genre. The result: clusters like "slow-burn prestige dramas", "high-octane crowd-pleasers", and "cerebral puzzle films" emerge naturally from the data.

### 4. Radar Chart Comparisons
Pull any two films and render a radar chart across the 10 core dimensions. *Inception* vs *Interstellar* hits different when you're looking at `cognitive_requirement` vs `immersive` side-by-side.

---

## 🛠️ How It Was Built

### The Data Pipeline

Since no dataset like this exists publicly, the data was bootstrapped using **Gemini 2.5 Flash as a structured evaluator**. A strict Pydantic schema constrains every response to a fixed set of fields and value ranges, making outputs consistent in shape even though the underlying judgments are the model's subjective read on each film.

```
[IMDb Top 1000 Titles]
        │
        ▼
[generate_profiles.py] ── Pydantic schema enforcement ──> structured JSON per film
        │
        ├── Retries on HTTP 429 with backoff
        ├── Incremental writes (safe to interrupt)
        └── Skips already-processed titles on resume
        │
        ▼
[run_profiler_loop.sh] ── rotates API keys on quota exhaustion
        │
        ▼
[cinatomy_movie_profiles.csv]   ← 1,000 rows × 27 columns
```

### Resource-Constrained Engineering

This was built entirely on free-tier API access. A few things worth noting about the pipeline design:

- `generate_profiles.py` writes results incrementally after each successful call — so if the process is interrupted at film #743, it resumes from #744 on the next run rather than starting over.
- On `HTTP 429` (rate limit), the script backs off 20 seconds and retries. On a second consecutive 429, it assumes the daily quota is exhausted and exits cleanly with code 0.
- `run_profiler_loop.sh` reads a pool of API keys from `api_keys.txt` and automatically rotates to the next key when the quota message appears in the output — fully unattended overnight runs.
- A 10-second sleep between requests keeps rolling TPM within free-tier limits.

The temperature is set to `0.2` — low, to minimize variance across runs, though not deterministic. Re-running the pipeline on the same title will likely produce very similar but not identical scores.

---

## 📊 Dataset Quick Stats

| Stat | Value |
|---|---|
| Films | 1,000 (IMDb Top 1000) |
| Columns | 27 |
| Missing values | 0 |
| Most common ending emotion | bittersweet (55.9%) |
| Most common ending structure | earned (67.2%) |
| `overall_feeling` distribution | 1% score ≤3 / 59.3% score 4 / 34.7% score 5 |

The heavy skew toward 4s and 5s is expected — this is IMDb's top-1000 list. The dataset is best suited for **relative comparisons** between acclaimed films, not for distinguishing good movies from bad ones.

---

## 🗂️ Repo Structure

```
cinatomy/
├── app.py                        # Streamlit application entry point
├── components/                   # Modular UI components (spider chart, scores)
├── data/                         # CSV datasets containing the 27 dimensions
├── pages/                        # Multi-page routing (Discover, Report Card)
├── styles/                       # Custom CSS for bohemian UI theme
├── utils/                        # Feature engineering and data loader
├── cinatomy_analysis.ipynb       # Original EDA and clustering analysis
└── README.md
```

---

## ⚡ Quickstart

### Explore the Dataset

```python
import pandas as pd
import ast

df = pd.read_csv("cinatomy_movie_profiles.csv")

# Parse list columns back to Python lists
df['plot_quality_reasons_for_liking'] = df['plot_quality_reasons_for_liking'].apply(ast.literal_eval)
df['plot_quality_reasons_for_disliking'] = df['plot_quality_reasons_for_disliking'].apply(ast.literal_eval)

print(df.shape)  # (1000, 27)
df.head()
```

### Find Your Next Watch by Vibe

```python
# High-energy films with low cognitive demand and an earned ending
perfect_friday_night = df[
    (df['pacing_efficiency'] >= 4) &
    (df['cognitive_requirement'] <= 2) &
    (df['end_feeling_structural_adjective'] == 'earned') &
    (df['end_feeling_emotional_adjective'] == 'energized')
][['movie_title', 'pacing_efficiency', 'cognitive_requirement', 'overall_feeling']]

print(perfect_friday_night.sort_values('overall_feeling', ascending=False))
```

### Extend the Dataset

```bash
# 1. Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/cinatomy
cd cinatomy
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt

# 2. Run the Web Application
streamlit run app.py
```

---

## ⚠️ Limitations

- **These are one LLM's opinions, not ground truth.** Scores reflect Gemini 2.5 Flash's read based on its training data — not aggregated human ratings, and not validated against real viewers (yet).
- **The source list skews acclaimed.** All 1,000 films are from IMDb's top-rated titles, so scores skew positive across most dimensions.
- **Low temperature ≠ deterministic.** Re-running the pipeline may produce slightly different values for some films.
- This is v0.1. The schema, dimensions, and film selection are all open to revision.

---

## 🔮 What's Next

This is being shared as a proof of concept to gauge interest. If it resonates, the natural next steps are:

- **Crowdsourced calibration layer** — letting real people rate films on these same dimensions to compare against the LLM baseline
- **Mood query interface** — filter by sliding across dimensions to find films by feel, not just genre
- **Expanded coverage** — moving beyond IMDb Top 1000 to cover more recent releases, international cinema, and cult favorites
- **Multi-model comparison** — running the same schema through different LLMs to study inter-model agreement (and disagreement)

---

## 🤝 Contributing

Issues and PRs are welcome, especially for:
- Suggesting new experiential dimensions worth adding to the schema
- Identifying films in the dataset with obviously wrong scores
- Ideas for the mood-query interface

---

## 👥 Built By

[Your name(s) here] — built in public, open to feedback, collaborators, and criticism.

⭐ If this framing seems useful, a star helps gauge whether it's worth building further.

---

## 📄 License

MIT — use the data, modify the pipeline, build on it freely. Attribution appreciated.
