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
from workout_generator import generate_workout, save_workout, get_user_saved_workouts


# Page config

st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="💪",
    layout="wide"
)


# Load and cache data

@st.cache_data
def get_data():
    df_users, df_logs = load_data()
    df_users["equipment"]          = df_users["equipment"].apply(ast.literal_eval)
    df_users["preferred_workouts"] = df_users["preferred_workouts"].apply(ast.literal_eval)
    return df_users, df_logs


df_users, df_logs = get_data()


# Sidebar navigation

st.sidebar.title("Navigation")
page = st.sidebar.radio("View", ["Global Dashboard", "User Dashboard"])

if page == "User Dashboard":
    user_num = st.sidebar.number_input(
        "Enter user number (1-500)",
        min_value=1,
        max_value=500,
        value=1
    )
    user_id = f"u_{user_num:04d}"


# Global Dashboard

if page == "Global Dashboard":
    st.title("AI Fitness Tracker")
    st.subheader("Global Overview — All Users")
    st.divider()

    summary = global_summary(df_logs)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Daily Steps",      f"{summary['avg_daily_steps']:,}")
    col2.metric("Avg Daily Calories",   f"{summary['avg_daily_calories']} kcal")
    col3.metric("Avg Workout Duration", f"{summary['avg_workout_duration']} min")
    col4.metric("Most Popular Workout", summary['most_popular_workout'])

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.pyplot(plot_calories_by_workout(df_logs))
    with col_right:
        st.pyplot(plot_workout_frequency(df_logs))


# User Dashboard

elif page == "User Dashboard":
    stats     = user_summary(user_id, df_users, df_logs)
    user_logs = df_logs[df_logs["user_id"] == user_id]
    recent    = get_last_7_days(user_id, df_logs)

    st.title(f"Dashboard — {stats['name']}")
    st.divider()

    # Profile
    st.subheader("Profile")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Age",           stats["age"])
    col2.metric("Goal",          stats["goal"].replace("_", " ").title())
    col3.metric("Fitness Level", stats["fitness_level"].title())
    col4.metric("Days Logged",   stats["total_days_logged"])

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**Equipment**")
        st.write(", ".join(stats["equipment"]))
    with col_right:
        st.markdown("**Preferred Workouts**")
        st.write(", ".join(stats["preferred_workouts"]))

    if stats["has_injuries"]:
        st.warning("This user has recorded injuries.")

    st.divider()

    # Activity summary
    st.subheader("Activity Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Daily Steps",      f"{stats['avg_daily_steps']:,}")
    col2.metric("Avg Daily Calories",   f"{stats['avg_daily_calories']} kcal")
    col3.metric("Avg Workout Duration", f"{stats['avg_workout_duration']} min")
    col4.metric("Favourite Workout",    stats["favourite_workout"])

    st.divider()

    # Charts
    st.subheader("Progress Over Time")
    st.pyplot(plot_steps_over_time(user_logs, stats["name"]))
    st.pyplot(plot_calories_over_time(user_logs, stats["name"]))
    st.pyplot(plot_user_workout_frequency(user_logs, stats["name"]))

    st.divider()

        # Workout suggestion
    st.subheader("Today's Workout Suggestion")

    # Button and card styling
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
            width: 100%;
            font-size: 1rem;
            padding: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialise session state
    if "workout" not in st.session_state:
        st.session_state.workout  = None
    if "rejected" not in st.session_state:
        st.session_state.rejected = []

    # Show saved workouts if any exist
    saved = get_user_saved_workouts(user_id)
    if saved:
        st.markdown(f"You have **{len(saved)}** saved workout(s).")
        view_saved = st.toggle("View saved workouts instead")

        if view_saved:
            saved_labels     = [f"{i+1}. {w['workout_summary']}" for i, w in enumerate(saved)]
            selected         = st.selectbox("Select a saved workout", saved_labels)
            selected_index   = saved_labels.index(selected)
            selected_workout = saved[selected_index]

            st.markdown(f"**{selected_workout['workout_summary']}**")
            for ex in selected_workout["exercises"]:
                with st.container(border=True):
                    st.markdown(f"**{ex['name']}**")
                    st.write(f"{ex['sets']} sets x {ex['reps']} reps — {ex['equipment']}")
                    st.caption(f"Muscle group: {ex['muscle_group']}")
                    st.caption(f"Notes: {ex['notes']}")
            st.stop()

    # Generate button — centred and prominent
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        if st.button("⚡ Generate Today's Workout", type="primary", use_container_width=True):
            with st.spinner("Generating your personalised workout..."):
                st.session_state.workout  = generate_workout(stats, recent)
                st.session_state.rejected = []

    if st.session_state.workout:
        workout = st.session_state.workout
        st.markdown(f"**{workout['workout_summary']}**")
        st.divider()

        # Render each exercise card
        for ex in workout["exercises"]:
            is_rejected = ex["name"] in st.session_state.rejected

            with st.container(border=True):
                col_info, col_btn = st.columns([4, 1])

                with col_info:
                    # Strike through name and dim the card if rejected
                    if is_rejected:
                        st.markdown(f"~~**{ex['name']}**~~ 🚫 *marked for replacement*")
                    else:
                        st.markdown(f"**{ex['name']}**")
                    st.write(f"{ex['sets']} sets x {ex['reps']} reps — {ex['equipment']}")
                    st.caption(f"Muscle group: {ex['muscle_group']}")
                    st.caption(f"Notes: {ex['notes']}")

                with col_btn:
                    if is_rejected:
                        # Allow user to undo rejection
                        if st.button("↩️ Undo", key=f"undo_{ex['name']}", use_container_width=True):
                            st.session_state.rejected.remove(ex["name"])
                            st.rerun()
                    else:
                        if st.button("👎 Reject", key=f"reject_{ex['name']}", use_container_width=True):
                            st.session_state.rejected.append(ex["name"])
                            st.rerun()

        st.divider()

        # Action buttons — centred
        col_left, col_mid_1, col_mid_2, col_right = st.columns([1, 2, 2, 1])

        with col_mid_1:
            if st.session_state.rejected:
                if st.button("🔄 Regenerate Rejected", type="primary", use_container_width=True):
                    with st.spinner("Updating your workout..."):
                        st.session_state.workout = generate_workout(
                            stats, recent, st.session_state.rejected
                        )
                        st.session_state.rejected = []
                        st.rerun()

        with col_mid_2:
            if st.button("💾 Save Workout", type="primary", use_container_width=True):
                save_workout(user_id, workout)
                st.success("Workout saved!")