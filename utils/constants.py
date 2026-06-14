"""Constants for the Cinatomy application.

Defines feature maps, color palette, score colors, feature groups, and quick presets.
"""

# 8 primary features for the spider/radar chart
SPIDER_FEATURES = [
    ("plot_quality_rating", "Plot Quality"),
    ("performance_of_actors", "Acting"),
    ("dialogues", "Dialogues"),
    ("visuals", "Visuals"),
    ("immersive", "Immersion"),
    ("impactful", "Impact"),
    ("originality", "Originality"),
    ("pacing_efficiency", "Pacing"),
]

# All 21 numeric features with display names
ALL_NUMERIC_FEATURES = [
    ("pacing_efficiency", "Pacing"),
    ("originality", "Originality"),
    ("family_friendly", "Family Friendly"),
    ("plot_quality_rating", "Plot Quality"),
    ("dialogues", "Dialogues"),
    ("end_feeling_ending_rating", "Ending"),
    ("immersive", "Immersion"),
    ("impactful", "Impact"),
    ("overall_feeling", "Overall Feeling"),
    ("visuals", "Visuals"),
    ("visual_effects", "VFX"),
    ("sound_bgm_quality", "BGM Quality"),
    ("sound_song_tracks_quality", "Soundtrack"),
    ("performance_of_actors", "Acting"),
    ("connected", "Emotional Connection"),
    ("references_contained", "References"),
    ("cognitive_requirement", "Cognitive Demand"),
    ("technical_knowledge_required", "Technical Barrier"),
    ("photosensitivity_warnings", "Photosensitivity"),
    ("animal_harm", "Animal Harm"),
    ("trailer_or_spoiler", "Spoiler Risk"),
]

# Features grouped by category for the breakdown display
FEATURE_GROUPS = {
    "Story & Writing": [
        ("plot_quality_rating", "Plot Quality"),
        ("dialogues", "Dialogues"),
        ("end_feeling_ending_rating", "Ending"),
        ("originality", "Originality"),
    ],
    "Craft & Production": [
        ("visuals", "Visuals"),
        ("visual_effects", "VFX"),
        ("sound_bgm_quality", "BGM Quality"),
        ("sound_song_tracks_quality", "Soundtrack"),
        ("performance_of_actors", "Acting"),
    ],
    "Experience": [
        ("immersive", "Immersion"),
        ("impactful", "Impact"),
        ("pacing_efficiency", "Pacing"),
        ("overall_feeling", "Overall Feeling"),
        ("connected", "Emotional Connection"),
    ],
    "Accessibility & Content": [
        ("family_friendly", "Family Friendly"),
        ("cognitive_requirement", "Cognitive Demand"),
        ("technical_knowledge_required", "Technical Barrier"),
        ("photosensitivity_warnings", "Photosensitivity"),
        ("animal_harm", "Animal Harm"),
        ("references_contained", "References"),
        ("trailer_or_spoiler", "Spoiler Risk"),
    ],
}

# Design system color palette
COLOR_PALETTE = {
    "primary": "#849C8A",
    "secondary": "#788E7E",
    "background": "#FDFBF7",
    "surface": "#F9F5EB",
    "text": "#3C2A21",
    "muted": "#8E7C71",
    "border": "#E8DFD0",
    "success": "#849C8A",
    "warning": "#D1A27A",
    "danger": "#C35B48",
    "blue": "#849C8A",
    "orange": "#C35B48",
}


def score_color(score):
    """Return a hex color for a given score (1-5)."""
    if score >= 5:
        return COLOR_PALETTE["success"]
    elif score >= 4:
        return COLOR_PALETTE["blue"]
    elif score >= 3:
        return COLOR_PALETTE["warning"]
    elif score >= 2:
        return COLOR_PALETTE["orange"]
    else:
        return COLOR_PALETTE["danger"]


def render_stars(score, max_score=5):
    """Return HTML string of filled and hollow stars for a 1-5 score."""
    filled = round(float(score))
    filled = max(0, min(filled, max_score))
    return ("★" * filled) + ("☆" * (max_score - filled))


# Quick presets for the Discover page search
# Each preset is a dict of feature_column -> (min_val, max_val)
QUICK_PRESETS = {
    "Crowd-Pleaser": {
        "plot_quality_rating": (4, 5),
        "overall_feeling": (4, 5),
        "performance_of_actors": (4, 5),
    },
    "Mind-Bender": {
        "cognitive_requirement": (4, 5),
        "originality": (4, 5),
        "plot_quality_rating": (4, 5),
    },
    "Visual Feast": {
        "visuals": (4, 5),
        "visual_effects": (4, 5),
        "immersive": (4, 5),
    },
    "Family Night": {
        "family_friendly": (3, 5),
        "photosensitivity_warnings": (1, 2),
        "animal_harm": (1, 1),
    },
    "Hidden Gems": {
        "originality": (4, 5),
        "overall_feeling": (4, 5),
        "connected": (4, 5),
    },
}
