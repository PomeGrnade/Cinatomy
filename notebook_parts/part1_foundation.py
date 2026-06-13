# %% [markdown]
# # 🎬 Cinatomy: Mapping the Experiential DNA of 1,000 Movies
# 
# Traditional movie metadata (cast, genre, budget, box office) tells us the basic facts, but it doesn't capture what it **FEELS** like to watch a film. 
# 
# This notebook explores **Cinatomy**, an experimental dataset that reframes 1,000 IMDb top-rated movies along ~20 experiential dimensions: pacing, emotional payoff, sensory load, cognitive demand, and more.
# 
# > **Important Note:** The data in this dataset is LLM-generated (Gemini 2.5 Flash) subjective scoring — not human crowdsourced ratings. The scores generally skew positive because these are IMDb's top 1000 films. This analysis is about the relative comparison between acclaimed films, not separating good from bad movies.
# 
# Our goals:
# 1. **Decode the `overall_feeling` formula:** Which experiential factors are weighed most heavily when forming an overall impression?
# 2. **Cluster movies by experiential vibe:** Can we group films by how they feel and build a recommendation system from that?

# %%
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Global Style settings
PALETTE = 'mako'
ACCENT_COLORS = ['#00d2ff', '#7b2ff7', '#ff6b6b', '#ffd93d', '#6bff9e', '#ff9edb']
sns.set_theme(style='darkgrid', palette=PALETTE, font_scale=1.1)
plt.rcParams.update({
    'figure.figsize': (12, 6),
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.dpi': 100,
    'figure.facecolor': '#0e1117',
    'axes.facecolor': '#0e1117',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white'
})

# %% [markdown]
# ## 2. Setup & Data Loading
# We start by loading the dataset, parsing the list-based columns, and checking for missing values.

# %%
df = pd.read_csv('data/cinatomy_imdb_top_1000.csv')

# Parse string representations of lists back into actual Python lists
df['plot_quality_reasons_for_liking'] = df['plot_quality_reasons_for_liking'].apply(ast.literal_eval)
df['plot_quality_reasons_for_disliking'] = df['plot_quality_reasons_for_disliking'].apply(ast.literal_eval)

print(f"Dataset shape: {df.shape}")
display(df.head(3))
display(df.info())
display(df.describe().round(2))

print("\nOverall Feeling Distribution:")
display(df['overall_feeling'].value_counts().sort_index())

# %% [markdown]
# **Observation:** We have 1,000 movies × 27 columns with zero missing values. 94% of the `overall_feeling` scores are 4 or 5, reflecting the positive skew expected from a top-1000 list.

# %% [markdown]
# ## 3. Preprocessing & Feature Engineering
# Let's encode the categorical features, one-hot encode the list reasons, and create several composite features that summarize related dimensions.

# %%
# 3a. Encode categoricals
emo_map = {'disappointed': 1, 'sad': 2, 'bittersweet': 3, 'neutral': 4, 'happy': 5, 'energized': 6}
struc_map = {'abrupt': 1, 'rushed': 2, 'ambiguous': 3, 'satisfying': 4, 'earned': 5}

df['emotional_adj_encoded'] = df['end_feeling_emotional_adjective'].map(emo_map)
df['structural_adj_encoded'] = df['end_feeling_structural_adjective'].map(struc_map)
df['audio_balance_binary'] = df['sound_audio_balance_issue'].astype(int)

# 3b. One-hot encode plot quality reasons
for reason in ['unpredictable', 'plot_twists', 'strong_pacing', 'tight_structure']:
    df[f'like_{reason}'] = df['plot_quality_reasons_for_liking'].apply(lambda x: int(reason in x))

for reason in ['predictable', 'cliche', 'narrative_inconsistency', 'plot_holes']:
    df[f'dislike_{reason}'] = df['plot_quality_reasons_for_disliking'].apply(lambda x: int(reason in x))

df['n_reasons_liked'] = df['plot_quality_reasons_for_liking'].apply(len)
df['n_reasons_disliked'] = df['plot_quality_reasons_for_disliking'].apply(len)

# 3c. Derived composite features
df['sound_composite'] = (df['sound_bgm_quality'] + df['sound_song_tracks_quality']) / 2
df['ending_composite'] = (df['end_feeling_ending_rating'] + df['structural_adj_encoded'] + df['emotional_adj_encoded']) / 3
df['craft_score'] = (df['visuals'] + df['visual_effects'] + df['sound_composite'] + df['performance_of_actors']) / 4
df['story_score'] = (df['plot_quality_rating'] + df['dialogues'] + df['originality'] + df['pacing_efficiency']) / 4
df['engagement_score'] = (df['immersive'] + df['impactful'] + df['connected']) / 3
df['accessibility'] = (df['family_friendly'] + (6 - df['cognitive_requirement']) + (6 - df['technical_knowledge_required'])) / 3

# Define shared variable lists for later sections
RADAR_DIMS = ['pacing_efficiency', 'originality', 'immersive', 'impactful', 'dialogues',
              'visuals', 'cognitive_requirement', 'family_friendly', 'performance_of_actors', 'ending_composite']

FEATURE_COLS = ['pacing_efficiency', 'originality', 'family_friendly', 'plot_quality_rating', 'dialogues',
                'end_feeling_ending_rating', 'immersive', 'impactful', 'visuals', 'visual_effects',
                'performance_of_actors', 'connected', 'references_contained', 'cognitive_requirement',
                'technical_knowledge_required', 'photosensitivity_warnings', 'animal_harm', 'trailer_or_spoiler',
                'emotional_adj_encoded', 'structural_adj_encoded', 'audio_balance_binary',
                'sound_bgm_quality', 'sound_song_tracks_quality',
                'like_unpredictable', 'like_plot_twists', 'like_strong_pacing', 'like_tight_structure',
                'dislike_predictable', 'dislike_cliche', 'dislike_narrative_inconsistency', 'dislike_plot_holes',
                'n_reasons_liked', 'n_reasons_disliked',
                'sound_composite', 'ending_composite', 'craft_score', 'story_score', 'engagement_score', 'accessibility']

# %% [markdown]
# **Observation:** We now have a robust set of numeric features, including meaningful composites like `craft_score` and `accessibility`, ready for analysis.

# %% [markdown]
# ## 4. Exploratory Data Analysis
# Let's visualize the distributions of our key features and see how they correlate with each other.

# %%
# 4a. Distribution Gallery
original_numeric_cols = ['pacing_efficiency', 'originality', 'family_friendly', 'plot_quality_rating', 'dialogues',
                         'end_feeling_ending_rating', 'immersive', 'impactful', 'overall_feeling', 'visuals', 
                         'visual_effects', 'performance_of_actors', 'connected', 'references_contained', 
                         'cognitive_requirement', 'technical_knowledge_required', 'photosensitivity_warnings', 
                         'animal_harm', 'trailer_or_spoiler', 'sound_bgm_quality', 'sound_song_tracks_quality']

fig, axes = plt.subplots(5, 5, figsize=(22, 20))
axes = axes.flatten()

for i, col in enumerate(original_numeric_cols):
    sns.histplot(df[col], ax=axes[i], bins=5, color=ACCENT_COLORS[0], discrete=True)
    axes[i].set_title(col.replace('_', ' ').title())
    axes[i].set_xlabel('')

for j in range(len(original_numeric_cols), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# %% [markdown]
# **Observation:** Many features like `performance_of_actors` and `plot_quality_rating` have very little variance (mostly 4s and 5s). Others like `family_friendly` and `visual_effects` are more spread out.

# %%
# 4b. Target Deep-Dive
plt.figure(figsize=(8, 5))
ax = sns.countplot(data=df, x='overall_feeling', palette=[ACCENT_COLORS[0]])
plt.title('Distribution of Overall Feeling (Target Variable)')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='baseline', fontsize=12, color='white', xytext=(0, 5), textcoords='offset points')
plt.show()

# %% [markdown]
# **Observation:** The modeling task is really: *what separates a 4 from a 5?* 

# %%
# 4c. Correlation Heatmap
plt.figure(figsize=(16, 14))
corr = df[original_numeric_cols].corr(method='spearman')
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='mako', vmin=-1, vmax=1, center=0)
plt.title('Spearman Correlation Matrix — Experiential Dimensions')
plt.show()

# %% [markdown]
# **Observation:** `overall_feeling` strongly correlates with `impactful`, `immersive`, and `plot_quality_rating`. `immersive` and `impactful` also correlate strongly with each other, suggesting movies that pull you in also hit hard emotionally.

# %%
# 4d. Categorical Frequency Charts
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.countplot(data=df, x='end_feeling_emotional_adjective', order=df['end_feeling_emotional_adjective'].value_counts().index, ax=axes[0], palette=[ACCENT_COLORS[1]])
axes[0].set_title('Ending Emotional Adjectives')
axes[0].tick_params(axis='x', rotation=45)

sns.countplot(data=df, x='end_feeling_structural_adjective', order=df['end_feeling_structural_adjective'].value_counts().index, ax=axes[1], palette=[ACCENT_COLORS[2]])
axes[1].set_title('Ending Structural Adjectives')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# %% [markdown]
# **Observation:** "Bittersweet" and "Happy" are the most common emotional endings. The vast majority of top 1000 films have endings structurally rated as "Earned" or "Satisfying".

# %%
# 4e. Plot Quality Reasons Breakdown
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

like_cols = ['like_unpredictable', 'like_plot_twists', 'like_strong_pacing', 'like_tight_structure']
like_sums = df[like_cols].sum().sort_values(ascending=False)
sns.barplot(x=like_sums.values, y=[col.replace('like_', '').replace('_', ' ').title() for col in like_sums.index], ax=axes[0], color=ACCENT_COLORS[3])
axes[0].set_title('Most Common Reasons for Liking the Plot')

dislike_cols = ['dislike_predictable', 'dislike_cliche', 'dislike_narrative_inconsistency', 'dislike_plot_holes']
dislike_sums = df[dislike_cols].sum().sort_values(ascending=False)
sns.barplot(x=dislike_sums.values, y=[col.replace('dislike_', '').replace('_', ' ').title() for col in dislike_sums.index], ax=axes[1], color=ACCENT_COLORS[4])
axes[1].set_title('Most Common Reasons for Disliking the Plot')

plt.tight_layout()
plt.show()

# %% [markdown]
# **Observation:** Nearly all top-1000 films have tight structure — it's table stakes. The differentiators for a great plot seem to be strong pacing and unpredictability. For dislikes, predictability is the most common critique.

# %% [markdown]
# ## 5. Movie Report Card — Radar Charts
# This is the visual centerpiece. We can compare the "Experiential DNA" of different movies using radar charts.

# %%
def movie_radar(titles, dimensions=None, title=None):
    """
    Renders overlapping Plotly radar charts for 1-4 movies.
    Uses RADAR_DIMS by default.
    """
    if dimensions is None:
        dimensions = RADAR_DIMS
    
    fig = go.Figure()
    for i, movie_title in enumerate(titles):
        row = df[df['movie_title'] == movie_title].iloc[0]
        values = [row[dim] for dim in dimensions]
        values += [values[0]]  # close the polygon
        dim_labels = [d.replace('_', ' ').title() for d in dimensions]
        dim_labels += [dim_labels[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=dim_labels,
            fill='toself',
            fillcolor=f'rgba({int(ACCENT_COLORS[i%len(ACCENT_COLORS)][1:3], 16)}, {int(ACCENT_COLORS[i%len(ACCENT_COLORS)][3:5], 16)}, {int(ACCENT_COLORS[i%len(ACCENT_COLORS)][5:7], 16)}, 0.15)',
            line=dict(color=ACCENT_COLORS[i%len(ACCENT_COLORS)], width=2.5),
            name=movie_title
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 6], showticklabels=True, color='rgba(255,255,255,0.3)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        title=dict(text=title or f"Experiential DNA: {' vs '.join(titles)}", font=dict(size=18)),
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        width=800,
        height=600,
        legend=dict(font=dict(size=13)),
        margin=dict(t=80, b=40)
    )
    fig.show()

# %%
movie_radar(['The Shawshank Redemption'], title='The #1 Film: What Does a Perfect Profile Look Like?')

# %% [markdown]
# **Observation:** The #1 IMDb movie has a near-maxed profile across pacing, plot quality, dialogues, immersive, and impactful dimensions, with lower visuals and cognitive requirement.

# %%
movie_radar(['The Dark Knight', '12 Angry Men'], title='Blockbuster Spectacle vs Chamber Drama')

# %% [markdown]
# **Observation:** *The Dark Knight* scores much higher on visuals, visual effects, and impactful dimensions, while *12 Angry Men* leans heavily on dialogues and cognitive requirement with almost zero visuals/VFX.

# %%
movie_radar(['Inception', 'Forrest Gump'], title='Mind-Bending Complexity vs Heartfelt Accessibility')

# %% [markdown]
# **Observation:** *Inception* pushes the cognitive requirement and originality boundaries, while *Forrest Gump* excels in family friendliness and emotional connection.

# %%
movie_radar(["Schindler's List", 'Pulp Fiction'], title='Emotional Devastation vs Stylistic Cool')

# %% [markdown]
# **Observation:** *Schindler's List* is heavily immersive and impactful, with an emotionally earned ending. *Pulp Fiction* is highly original with strong dialogues, but much lower on the emotional impact scale.
