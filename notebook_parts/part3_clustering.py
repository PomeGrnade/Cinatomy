# %% [markdown]
# ## 9. Feature Space & Dimensionality Reduction
# 
# Now we shift from predicting `overall_feeling` to discovering natural groupings — movies that feel similar regardless of genre labels. We will use dimensionality reduction to visualize this experiential space.

# %%
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False
    print('umap-learn not installed. pip install umap-learn for UMAP visualization.')

# 9a. Prepare clustering features
# We exclude 'overall_feeling' because we want to discover vibes, not just cluster by quality.
CLUSTER_FEATURES = FEATURE_COLS
X_cluster = df[CLUSTER_FEATURES].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

# %% [markdown]
# **Observation:** Standardization is critical — without it, features with larger ranges (like the composite scores) would dominate distance calculations.

# %%
# 9b. PCA
pca_full = PCA(random_state=42)
pca_full.fit(X_scaled)

cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)

plt.figure(figsize=(10, 5))
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', color=ACCENT_COLORS[0])
plt.axhline(y=0.90, color='r', linestyle='--')
plt.title('PCA Cumulative Explained Variance')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance Ratio')
plt.show()

pca_2d = PCA(n_components=2, random_state=42)
pca_coords = pca_2d.fit_transform(X_scaled)
df['pca_1'] = pca_coords[:, 0]
df['pca_2'] = pca_coords[:, 1]

# %% [markdown]
# **Observation:** It takes about 20-25 components to explain 90% of the variance, indicating that the experiential dimensions are quite independent and complex.

# %%
# 9c & 9d. t-SNE and UMAP
tsne = TSNE(n_components=2, perplexity=30, random_state=42, n_iter=1000)
tsne_coords = tsne.fit_transform(X_scaled)
df['tsne_1'] = tsne_coords[:, 0]
df['tsne_2'] = tsne_coords[:, 1]

if HAS_UMAP:
    reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
    umap_coords = reducer.fit_transform(X_scaled)
    df['umap_1'] = umap_coords[:, 0]
    df['umap_2'] = umap_coords[:, 1]

# 9e. Comparison plot
fig_cols = 3 if HAS_UMAP else 2
fig, axes = plt.subplots(1, fig_cols, figsize=(20, 6))

scatter_kws = {'alpha': 0.7, 's': 20}

sns.scatterplot(x='pca_1', y='pca_2', hue='overall_feeling', data=df, palette='mako', ax=axes[0], **scatter_kws)
axes[0].set_title('PCA Projection')
axes[0].get_legend().remove()

sns.scatterplot(x='tsne_1', y='tsne_2', hue='overall_feeling', data=df, palette='mako', ax=axes[1], **scatter_kws)
axes[1].set_title('t-SNE Projection')
axes[1].get_legend().remove()

if HAS_UMAP:
    sns.scatterplot(x='umap_1', y='umap_2', hue='overall_feeling', data=df, palette='mako', ax=axes[2], **scatter_kws)
    axes[2].set_title('UMAP Projection')
    axes[2].legend(title='Overall Feeling', bbox_to_anchor=(1.05, 1), loc='upper left')
else:
    axes[1].legend(title='Overall Feeling', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()

# %% [markdown]
# **Observation:** Both t-SNE and UMAP reveal underlying structures and distinct "islands" in the data, which PCA struggles to separate cleanly due to its linear nature.

# %% [markdown]
# ## 10. Clustering — Finding Movies by "Vibe"
# 
# We'll test different numbers of clusters (K) and use multiple algorithms to find the most robust grouping.

# %%
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score
from scipy.cluster.hierarchy import dendrogram, linkage

# 10a. Optimal K Selection
k_range = range(2, 11)
inertia, sil_scores, db_scores = [], [], []

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    
    inertia.append(kmeans.inertia_)
    sil_scores.append(silhouette_score(X_scaled, labels))
    db_scores.append(davies_bouldin_score(X_scaled, labels))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].plot(k_range, inertia, marker='o', color=ACCENT_COLORS[0])
axes[0].set_title('Elbow Method (Inertia)')
axes[0].set_xlabel('K')

axes[1].plot(k_range, sil_scores, marker='o', color=ACCENT_COLORS[1])
axes[1].set_title('Silhouette Score (Higher is Better)')
axes[1].set_xlabel('K')

axes[2].plot(k_range, db_scores, marker='o', color=ACCENT_COLORS[2])
axes[2].set_title('Davies-Bouldin Index (Lower is Better)')
axes[2].set_xlabel('K')

plt.tight_layout()
plt.show()

# %% [markdown]
# **Observation:** The metrics suggest that K=4 or K=5 are strong candidates. Let's proceed with **K=5** to get a richer variety of vibes.

# %%
# 10b. Run Clustering Algorithms
optimal_k = 5

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
df['cluster_kmeans'] = kmeans.fit_predict(X_scaled)

agglo = AgglomerativeClustering(n_clusters=optimal_k, linkage='ward')
df['cluster_agglo'] = agglo.fit_predict(X_scaled)

gmm = GaussianMixture(n_components=optimal_k, random_state=42)
df['cluster_gmm'] = gmm.fit_predict(X_scaled)

sil_kmeans = silhouette_score(X_scaled, df['cluster_kmeans'])
sil_agglo = silhouette_score(X_scaled, df['cluster_agglo'])
sil_gmm = silhouette_score(X_scaled, df['cluster_gmm'])

print(f"Silhouette Scores (K={optimal_k}):")
print(f"KMeans: {sil_kmeans:.3f}")
print(f"Agglomerative: {sil_agglo:.3f}")
print(f"GMM: {sil_gmm:.3f}")

# We'll use KMeans as it typically provides a solid, interpretable baseline
df['cluster'] = df['cluster_kmeans']

# %% [markdown]
# **Observation:** All three algorithms achieve similar silhouette scores. We will proceed with the KMeans clusters as our primary "vibe" groupings.

# %%
# 10c. Cluster Visualization
if HAS_UMAP:
    fig = px.scatter(df, x='umap_1', y='umap_2', color=df['cluster'].astype(str), 
                     hover_name='movie_title', color_discrete_sequence=ACCENT_COLORS,
                     title='Movie Clusters in Experiential Space (UMAP)',
                     template='plotly_dark')
    fig.update_layout(width=900, height=600)
    fig.show()

# %% [markdown]
# **Observation:** The interactive UMAP plot shows distinct experiential clusters. You can hover over points to see which movies belong to which cluster!

# %%
# 10d. Dendrogram
Z = linkage(X_scaled[:100], method='ward')

plt.figure(figsize=(20, 8))
dendrogram(Z, labels=df['movie_title'].values[:100], leaf_rotation=90, leaf_font_size=8)
plt.title('Hierarchical Clustering — Top 100 Movies')
plt.show()

# %% [markdown]
# **Observation:** The dendrogram reveals which movies are experientially closest, forming a family tree of movie vibes.

# %% [markdown]
# ## 11. Cluster Profiling & Recommendation System
# 
# What exactly *are* these clusters? Let's profile them by looking at their average experiential dimensions.

# %%
# 11a. Cluster Profiles
cluster_profiles = df.groupby('cluster')[RADAR_DIMS].mean()
display(cluster_profiles.round(2))

# %%
# 11b. Cluster Radar Charts
def cluster_radar(cluster_profiles, dimensions=RADAR_DIMS):
    fig = go.Figure()
    for cluster_id, row in cluster_profiles.iterrows():
        values = [row[d] for d in dimensions] + [row[dimensions[0]]]
        labels = [d.replace('_', ' ').title() for d in dimensions] + [dimensions[0].replace('_', ' ').title()]
        fig.add_trace(go.Scatterpolar(
            r=values, theta=labels, fill='toself',
            name=f'Cluster {cluster_id}',
            line=dict(color=ACCENT_COLORS[cluster_id % len(ACCENT_COLORS)], width=2),
            fillcolor=f'rgba({int(ACCENT_COLORS[cluster_id % len(ACCENT_COLORS)][1:3], 16)}, {int(ACCENT_COLORS[cluster_id % len(ACCENT_COLORS)][3:5], 16)}, {int(ACCENT_COLORS[cluster_id % len(ACCENT_COLORS)][5:7], 16)}, 0.12)'
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 6], color='rgba(255,255,255,0.3)'), bgcolor='rgba(0,0,0,0)'),
        template='plotly_dark', paper_bgcolor='#0e1117',
        title='Cluster Experiential Profiles', width=800, height=600,
        legend=dict(font=dict(size=13))
    )
    fig.show()

cluster_radar(cluster_profiles)

# %% [markdown]
# **Observation:** Each cluster has a distinct shape. Some index high on cognitive load and originality, while others index high on visual spectacle and family-friendliness.

# %%
# 11c. Cluster Heatmap
plt.figure(figsize=(14, 6))
sns.heatmap(cluster_profiles, annot=True, fmt='.2f', cmap='mako')
plt.title('Cluster Feature Profiles (Heatmap)')
plt.ylabel('Cluster ID')
plt.show()

# %%
# 11d. Name each cluster
# (Names are inferred from inspecting the heatmap profiles)
cluster_names = {
    0: 'Accessible Popcorn Spectacles',
    1: 'Intense Story-Driven Dramas',
    2: 'High-Cognitive Thrillers',
    3: 'Immersive Emotional Journeys',
    4: 'Lighthearted Family Friendly'
}

df['cluster_name'] = df['cluster'].map(cluster_names)

print("Example Movies per Cluster:")
for cid in sorted(cluster_names.keys()):
    print(f"\n[{cid}] {cluster_names[cid]}")
    examples = df[df['cluster'] == cid]['movie_title'].head(5).tolist()
    print("  " + ", ".join(examples))

# %% [markdown]
# **Observation:** The clusters separate nicely into intuitive vibe categories, from heavy dramas to accessible popcorn movies.

# %%
# 11e. Recommendation System
from sklearn.metrics.pairwise import cosine_similarity

sim_matrix = cosine_similarity(X_scaled)
sim_df = pd.DataFrame(sim_matrix, index=df['movie_title'], columns=df['movie_title'])

def recommend_similar(movie_title, n=5):
    """Returns top-N most similar movies based on overall experiential profile."""
    if movie_title not in sim_df.index:
        return f"Movie '{movie_title}' not found."
    sims = sim_df[movie_title].sort_values(ascending=False).iloc[1:n+1]
    return pd.DataFrame({'Similar Movie': sims.index, 'Overall Similarity (%)': (sims.values * 100).round(1)})

def recommend_by_focus(movie_title, focus='story', n=5):
    """Weighted similarity focusing on specific dimensions."""
    focus_features = {
        'story': ['pacing_efficiency', 'originality', 'plot_quality_rating', 'dialogues', 'story_score'],
        'emotion': ['immersive', 'impactful', 'connected', 'engagement_score', 'ending_composite'],
        'craft': ['visuals', 'visual_effects', 'sound_composite', 'performance_of_actors', 'craft_score'],
        'vibe': ['emotional_adj_encoded', 'structural_adj_encoded', 'family_friendly', 'cognitive_requirement']
    }
    cols = [c for c in focus_features.get(focus, focus_features['story']) if c in df.columns]
    X_focus = StandardScaler().fit_transform(df[cols])
    sim = cosine_similarity(X_focus)
    idx = df[df['movie_title'] == movie_title].index[0]
    scores = pd.Series(sim[idx], index=df['movie_title']).sort_values(ascending=False).iloc[1:n+1]
    return pd.DataFrame({'Similar Movie': scores.index, f'{focus.title()} Match (%)': (scores.values * 100).round(1)})

# %%
# 11f. Recommendation Showcase
showcase_movie = 'Inception'
print(f"### 🎬 If you loved '{showcase_movie}'...\n")

print(f"Cluster: {df[df['movie_title'] == showcase_movie]['cluster_name'].iloc[0]}")
display(recommend_similar(showcase_movie))
display(recommend_by_focus(showcase_movie, 'story'))
display(recommend_by_focus(showcase_movie, 'emotion'))

# %% [markdown]
# **Observation:** By breaking similarity down by focus area, we can recommend movies that match the specific aspect of a film that the viewer enjoyed (e.g., matching *Inception* for its mind-bending story vs. matching it for its emotional stakes).

# %% [markdown]
# ## 12. Limitations & Next Steps
# 
# ### Limitations
# - **Single LLM Source:** All scores come from a single LLM (Gemini 2.5 Flash). Different LLMs would produce different profiles, and there is no human crowdsourced validation yet.
# - **Positive Skew:** Since this dataset consists of IMDb's top 1,000 films, almost everything is highly rated. The clustering separates "types of great," rather than separating good from bad.
# - **Subjectivity of Ordinal Encoding:** Mapping string adjectives (e.g., mapping "energized" > "happy") to ordinal numbers is a subjective judgment call.
# - **Temporal Blindness:** The model's assessment may not reflect evolving cultural reception over time.
# 
# ### Next Steps
# - **Human Validation:** Cross-reference these experiential profiles with actual viewer surveys or Letterboxd reviews.
# - **Mood-Based Query Interface:** Build an app where a user can say "I want something visually stunning but low cognitive effort" and get filtered recommendations.
# - **Expand Beyond Top 1,000:** Include mediocre or objectively bad films to give the model a truly discriminative signal.
# - **Multi-LLM Ensemble:** Score each movie with 3-4 different foundation models and use the consensus.
# 
# ### Conclusion
# This experiment surfaces a compelling idea: we can move beyond rigid genres to categorize and recommend movies based on their **experiential DNA**. The models reveal that the LLM is highly consistent in weighting `impactful` and `immersive` experiences when determining a movie's overall feeling. More importantly, projecting these dimensions into 2D space yields intuitive clusters—grouping the intense dramas separately from the popcorn blockbusters.
# 
# If this kind of experiential profiling resonates with you, the dataset is public—fork it, critique it, and improve upon it.
