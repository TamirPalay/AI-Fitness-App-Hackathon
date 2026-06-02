"""
app.py
------
Streamlit dashboard for the AI Fitness Tracker.

Run from the project root:
    streamlit run src/app.py
"""

import ast
import streamlit as st
from analysis import load_data, global_summary, user_summary, last_7_days as get_last_7_days
from visualizations import (
    plot_calories_by_workout,
    plot_workout_frequency,
    plot_steps_over_time,
    plot_calories_over_time,
    plot_user_workout_frequency
)
from workout_generator import (
    generate_workout,
    save_workout,
    get_user_saved_workouts,
    get_user_injuries,
    get_user_liked_exercises
)
from muscle_map import plot_muscle_map


# Color palette — shared across cards and muscle map

ACCENT = "#0e7490"

MUSCLE_COLORS = {
    "chest":                   "#ef4444",
    "back":                    "#3b82f6",
    "legs":                    "#22c55e",
    "shoulders":               "#f97316",
    "arms":                    "#a855f7",
    "core":                    "#14b8a6",
    "cardio":                  "#eab308",
    "back and legs":           "#6366f1",
    "legs and cardiovascular": "#6366f1",
}


# Global CSS

def inject_css():
    st.markdown("""
        <style>

        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }

        /* Styled metric cards */
        div[data-testid="metric-container"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }

        /* Primary action buttons */
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #0e7490;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #0c6480;
        }

        /* All buttons */
        div[data-testid="stButton"] > button {
            border-radius: 8px;
            font-size: 0.9rem;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9;
        }

        /* Exercise card coloured header */
        .exercise-card-header {
            padding: 10px 12px 8px 12px;
            border-radius: 10px 10px 0 0;
            margin-bottom: 8px;
        }

        .exercise-name {
            font-size: 1rem;
            font-weight: 700;
            color: white;
            margin: 0 0 4px 0;
        }

        .muscle-badge {
            display: inline-block;
            background: rgba(255,255,255,0.25);
            color: white;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Workout summary banner */
        .workout-banner {
            background: linear-gradient(135deg, #0e7490, #0891b2);
            color: white;
            padding: 18px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        .workout-banner h3 {
            margin: 0 0 4px 0;
            font-size: 1.1rem;
            font-weight: 700;
        }

        .workout-banner p {
            margin: 0;
            font-size: 0.9rem;
            opacity: 0.85;
        }

        </style>
    """, unsafe_allow_html=True)


# Page config

st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="💪",
    layout="wide"
)

inject_css()


# Load and cache data

@st.cache_data
def get_data():
    df_users, df_logs = load_data()
    # CSV serialises lists as strings — convert back
    df_users["equipment"]          = df_users["equipment"].apply(ast.literal_eval)
    df_users["preferred_workouts"] = df_users["preferred_workouts"].apply(ast.literal_eval)
    return df_users, df_logs


df_users, df_logs = get_data()


# Sidebar

st.sidebar.title("💪 AI Fitness Tracker")
st.sidebar.divider()
page = st.sidebar.radio("Navigate", ["🌍 Global Dashboard", "👤 User Dashboard"])

if page == "👤 User Dashboard":
    user_num = st.sidebar.number_input(
        "Enter user number (1–500)",
        min_value=1,
        max_value=500,
        value=1
    )
    user_id = f"u_{user_num:04d}"

    # Show personalised summary in sidebar once a user is selected
    try:
        sidebar_stats = user_summary(user_id, df_users, df_logs)
        st.sidebar.divider()
        st.sidebar.markdown(f"**{sidebar_stats['name']}**")
        st.sidebar.caption(f"🎯 {sidebar_stats['goal'].replace('_', ' ').title()}")
        st.sidebar.caption(f"⚡ {sidebar_stats['fitness_level'].title()}")
        st.sidebar.caption(f"📅 {sidebar_stats['total_days_logged']} days logged")
    except Exception:
        pass


# Global Dashboard

if page == "🌍 Global Dashboard":
    st.title("🌍 Global Overview")
    st.caption("Aggregate statistics across all 500 users")
    st.divider()

    summary = global_summary(df_logs)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚶 Avg Daily Steps",      f"{summary['avg_daily_steps']:,}")
    col2.metric("🔥 Avg Daily Calories",   f"{summary['avg_daily_calories']} kcal")
    col3.metric("⏱️ Avg Workout Duration", f"{summary['avg_workout_duration']} min")
    col4.metric("🏆 Most Popular Workout", summary['most_popular_workout'])

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.pyplot(plot_calories_by_workout(df_logs))
    with col_right:
        st.pyplot(plot_workout_frequency(df_logs))


# User Dashboard

elif page == "👤 User Dashboard":
    stats     = user_summary(user_id, df_users, df_logs)
    user_logs = df_logs[df_logs["user_id"] == user_id]
    recent    = get_last_7_days(user_id, df_logs)
    injuries  = get_user_injuries(user_id)

    st.title(f"👤 {stats['name']}")
    st.caption(f"User {user_id}  ·  {stats['goal'].replace('_', ' ').title()}  ·  {stats['fitness_level'].title()}")
    st.divider()

    # Profile metrics
    st.subheader("Profile")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎂 Age",           stats["age"])
    col2.metric("🎯 Goal",          stats["goal"].replace("_", " ").title())
    col3.metric("⚡ Fitness Level", stats["fitness_level"].title())
    col4.metric("📅 Days Logged",   stats["total_days_logged"])

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**🏋️ Equipment**")
        equipment_list = [e.replace("_", " ").title() for e in stats["equipment"]]
        st.write(", ".join(equipment_list))
    with col_right:
        st.markdown("**❤️ Preferred Workouts**")
        st.write(", ".join(stats["preferred_workouts"]))

    # Injury details — pulled directly from users.json for full detail
    if injuries:
        st.warning("⚠️ This user has recorded injuries — the workout generator will account for these.")
        for injury in injuries:
            body_part = injury["body_part"].replace("_", " ").title()
            severity  = injury["severity"].replace("_", " ").title()
            st.caption(f"🩹 **{body_part}** — {severity}: {injury['notes']}")

    st.divider()

    # Activity summary metrics
    st.subheader("📊 Activity Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚶 Avg Daily Steps",      f"{stats['avg_daily_steps']:,}")
    col2.metric("🔥 Avg Daily Calories",   f"{stats['avg_daily_calories']} kcal")
    col3.metric("⏱️ Avg Workout Duration", f"{stats['avg_workout_duration']} min")
    col4.metric("🏆 Favourite Workout",    stats["favourite_workout"])

    st.divider()

    # Charts — steps and calories side by side, frequency centred below
    st.subheader("📈 Progress Over Time")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.pyplot(plot_steps_over_time(user_logs, stats["name"]))
    with chart_col2:
        st.pyplot(plot_calories_over_time(user_logs, stats["name"]))

    freq_left, freq_mid, freq_right = st.columns([1, 2, 1])
    with freq_mid:
        st.pyplot(plot_user_workout_frequency(user_logs, stats["name"]))

    st.divider()

    # Workout suggestion section
    st.subheader("⚡ Today's Workout")

    # Session state:
    # workout      — current generated workout dict
    # rejected     — exercises rejected in this round (cleared after regenerate)
    # all_rejected — all rejections this session (persisted to users.json on save)
    # all_liked    — all likes this session (persisted to users.json on save)
    if "workout" not in st.session_state:
        st.session_state.workout      = None
    if "rejected" not in st.session_state:
        st.session_state.rejected     = []
    if "all_rejected" not in st.session_state:
        st.session_state.all_rejected = []
    if "all_liked" not in st.session_state:
        st.session_state.all_liked    = []

    # Saved workouts toggle
    saved = get_user_saved_workouts(user_id)
    if saved:
        st.markdown(f"💾 You have **{len(saved)}** saved workout(s).")
        view_saved = st.toggle("View a saved workout instead")

        if view_saved:
            saved_labels     = [f"{i+1}. {w['workout_summary']}" for i, w in enumerate(saved)]
            selected         = st.selectbox("Select a saved workout", saved_labels)
            selected_index   = saved_labels.index(selected)
            selected_workout = saved[selected_index]

            st.markdown(f"""
                <div class="workout-banner">
                    <h3>💾 {selected_workout['workout_summary']}</h3>
                    <p>Saved workout</p>
                </div>
            """, unsafe_allow_html=True)

            # Muscle map for saved workout
            map_col, cards_col = st.columns([1, 3])
            with map_col:
                st.pyplot(plot_muscle_map(selected_workout["exercises"], MUSCLE_COLORS))

            with cards_col:
                cols = st.columns(3)
                for i, ex in enumerate(selected_workout["exercises"]):
                    color = MUSCLE_COLORS.get(ex["muscle_group"].lower(), ACCENT)
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"""
                                <div class="exercise-card-header" style="background:{color}">
                                    <p class="exercise-name">{ex['name']}</p>
                                    <span class="muscle-badge">{ex['muscle_group']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            st.write(f"**{ex['sets']} sets × {ex['reps']} reps**")
                            st.caption(f"🏋️ {ex['equipment'].replace('_', ' ').title()}")
                            st.caption(f"💡 {ex['notes']}")
            st.stop()

    # Feedback history expanders
    disliked = stats.get("disliked_exercises", [])
    if isinstance(disliked, str):
        disliked = ast.literal_eval(disliked)
    liked_history = get_user_liked_exercises(user_id)

    feedback_col1, feedback_col2 = st.columns(2)
    with feedback_col1:
        if disliked:
            with st.expander(f"🚫 {len(disliked)} previously disliked exercise(s)"):
                st.write(", ".join(disliked))
    with feedback_col2:
        if liked_history:
            with st.expander(f"❤️ {len(liked_history)} exercise(s) you enjoy"):
                st.write(", ".join(liked_history))

    # Generate button — centred
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        if st.button("⚡ Generate Today's Workout", type="primary", use_container_width=True):
            with st.spinner("Building your personalised workout..."):
                st.session_state.workout      = generate_workout(stats, recent)
                st.session_state.rejected     = []
                st.session_state.all_rejected = []
                st.session_state.all_liked    = []

    if st.session_state.workout:
        workout = st.session_state.workout

        # Workout summary banner
        num_exercises = len(workout["exercises"])
        est_duration  = num_exercises * 10
        st.markdown(f"""
            <div class="workout-banner">
                <h3>🏋️ {workout['workout_summary']}</h3>
                <p>{num_exercises} exercises  ·  ~{est_duration} min estimated</p>
            </div>
        """, unsafe_allow_html=True)

        # Muscle map left, exercise cards right
        map_col, cards_col = st.columns([1, 3])

        with map_col:
            # Body diagram — primary muscles vibrant, secondary lighter
            st.pyplot(plot_muscle_map(workout["exercises"], MUSCLE_COLORS))

        with cards_col:
            # Exercise grid — 3 cards per row
            cols = st.columns(3)
            for i, ex in enumerate(workout["exercises"]):
                is_rejected = ex["name"] in st.session_state.rejected
                is_liked    = ex["name"] in st.session_state.all_liked
                color       = MUSCLE_COLORS.get(ex["muscle_group"].lower(), ACCENT)

                with cols[i % 3]:
                    with st.container(border=True):

                        # Coloured header — greyed if rejected, heart if liked
                        if is_rejected:
                            st.markdown(f"""
                                <div class="exercise-card-header" style="background:#94a3b8">
                                    <p class="exercise-name">🚫 {ex['name']}</p>
                                    <span class="muscle-badge">marked for replacement</span>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            heart = "❤️ " if is_liked else ""
                            st.markdown(f"""
                                <div class="exercise-card-header" style="background:{color}">
                                    <p class="exercise-name">{heart}{ex['name']}</p>
                                    <span class="muscle-badge">{ex['muscle_group']}</span>
                                </div>
                            """, unsafe_allow_html=True)

                        st.write(f"**{ex['sets']} sets × {ex['reps']} reps**")
                        st.caption(f"🏋️ {ex['equipment'].replace('_', ' ').title()}")
                        st.caption(f"💡 {ex['notes']}")

                        # Undo button if rejected, like + reject buttons otherwise
                        if is_rejected:
                            if st.button("↩️ Undo", key=f"undo_{ex['name']}", use_container_width=True):
                                st.session_state.rejected.remove(ex["name"])
                                if ex["name"] in st.session_state.all_rejected:
                                    st.session_state.all_rejected.remove(ex["name"])
                                st.rerun()
                        else:
                            btn_like, btn_reject = st.columns(2)
                            with btn_like:
                                heart_label = "❤️ Liked" if is_liked else "🤍 Like"
                                if st.button(heart_label, key=f"like_{ex['name']}", use_container_width=True):
                                    if is_liked:
                                        st.session_state.all_liked.remove(ex["name"])
                                    else:
                                        st.session_state.all_liked.append(ex["name"])
                                    st.rerun()
                            with btn_reject:
                                if st.button("👎 Reject", key=f"reject_{ex['name']}", use_container_width=True):
                                    st.session_state.rejected.append(ex["name"])
                                    if ex["name"] not in st.session_state.all_rejected:
                                        st.session_state.all_rejected.append(ex["name"])
                                    st.rerun()

        st.divider()

        # Regenerate and save buttons — centred
        col_left, col_mid_1, col_mid_2, col_right = st.columns([1, 2, 2, 1])

        with col_mid_1:
            # Only show regenerate button when there are pending rejections
            if st.session_state.rejected:
                if st.button("🔄 Regenerate Rejected", type="primary", use_container_width=True):
                    with st.spinner("Swapping out exercises..."):
                        st.session_state.workout = generate_workout(
                            stats, recent,
                            st.session_state.rejected,
                            st.session_state.workout
                        )
                        st.session_state.rejected = []
                        st.rerun()

        with col_mid_2:
            if st.button("💾 Save Workout", type="primary", use_container_width=True):
                save_workout(
                    user_id,
                    workout,
                    st.session_state.all_rejected,
                    st.session_state.all_liked
                )
                st.session_state.all_rejected = []
                st.session_state.all_liked    = []
                st.success("Workout saved! Your feedback has been recorded. 🎉")