"""
muscle_map.py
-------------
Generates a front/back body diagram with active muscle groups highlighted.
Primary muscles shown in full color, secondary in a lighter shade.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, Circle, FancyBboxPatch


INACTIVE  = "#dde3ea"
OUTLINE   = "#9aa5b4"
SKIN_TONE = "#edf2f7"


# Muscle group normalization — maps LLM strings to standard keys

def normalize_muscle(mg: str) -> str:
    mg = mg.lower().strip()
    if any(w in mg for w in ["cardiovascular", "cardio"]):
        return "cardio"
    if any(w in mg for w in ["quad", "hamstring", "glute", "thigh", "calf", "leg"]):
        return "legs"
    if any(w in mg for w in ["lat", "trap", "rhomboid", "lumbar"]):
        return "back"
    if any(w in mg for w in ["bicep", "tricep", "forearm"]):
        return "arms"
    if any(w in mg for w in ["ab", "abdominal", "oblique", "core"]):
        return "core"
    if any(w in mg for w in ["delt", "rotator", "shoulder"]):
        return "shoulders"
    if "chest" in mg or "pec" in mg:
        return "chest"
    if "back" in mg:
        return "back"
    return mg


def parse_exercise_muscles(exercises: list) -> tuple:
    primary   = set()
    secondary = set()
    for ex in exercises:
        mg = ex.get("muscle_group", "").lower().strip()
        if " and " in mg:
            parts = [p.strip() for p in mg.split(" and ")]
            primary.add(normalize_muscle(parts[0]))
            for p in parts[1:]:
                secondary.add(normalize_muscle(p))
        else:
            primary.add(normalize_muscle(mg))
    secondary -= primary
    return primary, secondary


def lighten(hex_color: str, factor: float = 0.55) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_color(key: str, primary: set, secondary: set, muscle_colors: dict) -> str:
    if "cardio" in primary:
        return lighten(muscle_colors.get(key, INACTIVE), 0.3)
    if key in primary:
        return muscle_colors.get(key, INACTIVE)
    if key in secondary:
        return lighten(muscle_colors.get(key, INACTIVE), 0.55)
    return INACTIVE


# Patch helpers

def e(ax, cx, cy, rx, ry, color, zorder=2):
    """Ellipse patch."""
    ax.add_patch(Ellipse((cx, cy), rx*2, ry*2,
                         facecolor=color, edgecolor=OUTLINE,
                         linewidth=0.5, zorder=zorder))


def r(ax, x, y, w, h, color, radius=4, zorder=2):
    """Rounded rectangle patch."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=color, edgecolor=OUTLINE,
                                linewidth=0.5, zorder=zorder))


def c(ax, cx, cy, radius, color, zorder=2):
    """Circle patch."""
    ax.add_patch(Circle((cx, cy), radius,
                        facecolor=color, edgecolor=OUTLINE,
                        linewidth=0.5, zorder=zorder))


# Body drawing

def _setup_ax(ax, title):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 270)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8, color="#64748b", pad=3)


def draw_front(ax, primary, secondary, muscle_colors):
    _setup_ax(ax, "Front")
    cl = {k: get_color(k, primary, secondary, muscle_colors)
          for k in ["chest", "core", "shoulders", "arms", "legs", "back", "cardio"]}

    # --- Silhouette base (drawn back to front) ---

    # Torso silhouette
    e(ax, 50, 180, 30, 12, SKIN_TONE, zorder=1)            # hip ellipse
    r(ax, 30, 118, 40, 68, SKIN_TONE, radius=8, zorder=1)  # main torso

    # Shoulder caps
    e(ax, 22, 182, 16, 11, SKIN_TONE, zorder=1)
    e(ax, 78, 182, 16, 11, SKIN_TONE, zorder=1)

    # Upper arms (tall narrow ellipses — no more rectangles)
    e(ax, 15, 158, 9, 25, SKIN_TONE, zorder=1)
    e(ax, 85, 158, 9, 25, SKIN_TONE, zorder=1)

    # Forearms
    e(ax, 14, 112, 7, 22, SKIN_TONE, zorder=1)
    e(ax, 86, 112, 7, 22, SKIN_TONE, zorder=1)

    # Hands
    e(ax, 13, 83, 6, 8, SKIN_TONE, zorder=1)
    e(ax, 87, 83, 6, 8, SKIN_TONE, zorder=1)

    # Hips
    r(ax, 28, 103, 44, 18, SKIN_TONE, radius=6, zorder=1)

    # Thighs (tall ellipses)
    e(ax, 40, 72, 12, 28, SKIN_TONE, zorder=1)
    e(ax, 60, 72, 12, 28, SKIN_TONE, zorder=1)

    # Calves (narrower ellipses)
    e(ax, 40, 30, 9, 18, SKIN_TONE, zorder=1)
    e(ax, 60, 30, 9, 18, SKIN_TONE, zorder=1)

    # Neck
    r(ax, 45, 193, 10, 14, SKIN_TONE, radius=4, zorder=1)

    # Head
    c(ax, 50, 218, 18, SKIN_TONE, zorder=1)

    # --- Muscle group overlays ---

    # Shoulders
    e(ax, 22, 182, 14, 9, cl["shoulders"])
    e(ax, 78, 182, 14, 9, cl["shoulders"])

    # Chest (two overlapping pec ellipses)
    e(ax, 41, 172, 12, 10, cl["chest"])
    e(ax, 59, 172, 12, 10, cl["chest"])

    # Core / abs
    r(ax, 37, 128, 26, 35, cl["core"], radius=5)

    # Arms — biceps
    e(ax, 15, 162, 8, 18, cl["arms"])
    e(ax, 85, 162, 8, 18, cl["arms"])

    # Forearms — lighter shade of arms
    arm_light = lighten(cl["arms"], 0.3) if cl["arms"] != INACTIVE else INACTIVE
    e(ax, 14, 112, 6, 16, arm_light)
    e(ax, 86, 112, 6, 16, arm_light)

    # Legs — quads
    e(ax, 40, 76, 10, 22, cl["legs"])
    e(ax, 60, 76, 10, 22, cl["legs"])

    # Calves — lighter shade of legs
    leg_light = lighten(cl["legs"], 0.3) if cl["legs"] != INACTIVE else INACTIVE
    e(ax, 40, 30, 7, 14, leg_light)
    e(ax, 60, 30, 7, 14, leg_light)


def draw_back(ax, primary, secondary, muscle_colors):
    _setup_ax(ax, "Back")
    cl = {k: get_color(k, primary, secondary, muscle_colors)
          for k in ["chest", "core", "shoulders", "arms", "legs", "back", "cardio"]}

    # --- Silhouette base ---

    e(ax, 50, 180, 30, 12, SKIN_TONE, zorder=1)
    r(ax, 30, 118, 40, 68, SKIN_TONE, radius=8, zorder=1)
    e(ax, 22, 182, 16, 11, SKIN_TONE, zorder=1)
    e(ax, 78, 182, 16, 11, SKIN_TONE, zorder=1)
    e(ax, 15, 158, 9, 25, SKIN_TONE, zorder=1)
    e(ax, 85, 158, 9, 25, SKIN_TONE, zorder=1)
    e(ax, 14, 112, 7, 22, SKIN_TONE, zorder=1)
    e(ax, 86, 112, 7, 22, SKIN_TONE, zorder=1)
    e(ax, 13, 83, 6, 8, SKIN_TONE, zorder=1)
    e(ax, 87, 83, 6, 8, SKIN_TONE, zorder=1)
    r(ax, 28, 103, 44, 18, SKIN_TONE, radius=6, zorder=1)
    e(ax, 40, 72, 12, 28, SKIN_TONE, zorder=1)
    e(ax, 60, 72, 12, 28, SKIN_TONE, zorder=1)
    e(ax, 40, 30, 9, 18, SKIN_TONE, zorder=1)
    e(ax, 60, 30, 9, 18, SKIN_TONE, zorder=1)
    r(ax, 45, 193, 10, 14, SKIN_TONE, radius=4, zorder=1)
    c(ax, 50, 218, 18, SKIN_TONE, zorder=1)

    # --- Muscle overlays ---

    # Rear delts / shoulders
    e(ax, 22, 182, 14, 9, cl["shoulders"])
    e(ax, 78, 182, 14, 9, cl["shoulders"])

    # Traps (upper back)
    e(ax, 40, 185, 12, 7, cl["back"])
    e(ax, 60, 185, 12, 7, cl["back"])

    # Lats (large back muscles)
    e(ax, 38, 158, 10, 22, cl["back"])
    e(ax, 62, 158, 10, 22, cl["back"])

    # Lower back
    r(ax, 38, 122, 24, 18, cl["back"], radius=4)

    # Triceps
    e(ax, 15, 158, 8, 18, cl["arms"])
    e(ax, 85, 158, 8, 18, cl["arms"])

    # Forearms
    arm_light = lighten(cl["arms"], 0.3) if cl["arms"] != INACTIVE else INACTIVE
    e(ax, 14, 112, 6, 16, arm_light)
    e(ax, 86, 112, 6, 16, arm_light)

    # Glutes
    e(ax, 41, 108, 11, 9, cl["legs"])
    e(ax, 59, 108, 11, 9, cl["legs"])

    # Hamstrings
    e(ax, 40, 70, 10, 22, cl["legs"])
    e(ax, 60, 70, 10, 22, cl["legs"])

    # Calves
    leg_light = lighten(cl["legs"], 0.3) if cl["legs"] != INACTIVE else INACTIVE
    e(ax, 40, 30, 7, 14, leg_light)
    e(ax, 60, 30, 7, 14, leg_light)


# Main function

def plot_muscle_map(exercises: list, muscle_colors: dict) -> plt.Figure:
    primary, secondary = parse_exercise_muscles(exercises)

    fig, (ax_front, ax_back) = plt.subplots(
        1, 2, figsize=(4.5, 6.5),
        facecolor="white"
    )
    fig.subplots_adjust(wspace=0.05, bottom=0.1)

    draw_front(ax_front, primary, secondary, muscle_colors)
    draw_back(ax_back,  primary, secondary, muscle_colors)

    # Legend — only show active muscle groups
    patches = []
    for mg in sorted(primary | secondary):
        if mg == "cardio":
            continue
        color = muscle_colors.get(mg, INACTIVE)
        if mg in secondary:
            color = lighten(color, 0.55)
        label = f"{mg.title()} {'(2°)' if mg in secondary else ''}"
        patches.append(mpatches.Patch(facecolor=color, edgecolor=OUTLINE, label=label))

    if patches:
        fig.legend(handles=patches, loc="lower center", ncol=3,
                   fontsize=7, frameon=False, bbox_to_anchor=(0.5, 0.01))

    return fig