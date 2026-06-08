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
    get_user_liked_exercises,
    generate_exercise_pool
)
from muscle_map import plot_muscle_map
@st.cache_data
def cached_plot_steps(user_id, name):
    user_logs = df_logs[df_logs["user_id"] == user_id]
    return plot_steps_over_time(user_logs, name)

@st.cache_data
def cached_plot_calories(user_id, name):
    user_logs = df_logs[df_logs["user_id"] == user_id]
    return plot_calories_over_time(user_logs, name)

@st.cache_data
def cached_plot_freq(user_id, name):
    user_logs = df_logs[df_logs["user_id"] == user_id]
    return plot_user_workout_frequency(user_logs, name)

@st.cache_data
def cached_plot_global_calories():
    return plot_calories_by_workout(df_logs)

@st.cache_data
def cached_plot_global_freq():
    return plot_workout_frequency(df_logs)

# Color palette

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

PILL_COLORS = ["#ef4444","#3b82f6","#22c55e","#f97316","#a855f7","#14b8a6","#eab308"]


# Helpers

def truncate(text: str, limit: int = 72) -> str:
    return text[:limit] + "…" if len(text) > limit else text

def hex_lighten(hex_color: str, factor: float = 0.88) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"#{int(r+(255-r)*factor):02x}{int(g+(255-g)*factor):02x}{int(b+(255-b)*factor):02x}"


# CSS

def inject_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

        div[data-testid="metric-container"] {
            background-color:#f8fafc; border:1px solid #e2e8f0;
            border-radius:12px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.06);
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color:#0e7490; border:none; border-radius:8px;
            font-weight:600; letter-spacing:0.3px;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover { background-color:#0c6480; }
        div[data-testid="stButton"] > button { border-radius:8px; font-size:0.9rem; }
        section[data-testid="stSidebar"] { background-color:#f1f5f9; }

        .exercise-card-header { padding:10px 12px 8px 12px; border-radius:10px 10px 0 0; margin-bottom:8px; }
        .exercise-name { font-size:1rem; font-weight:700; color:white; margin:0 0 4px 0; }
        .muscle-badge {
            display:inline-block; background:rgba(255,255,255,0.25); color:white;
            font-size:0.7rem; font-weight:600; padding:2px 8px;
            border-radius:20px; text-transform:uppercase; letter-spacing:0.5px;
        }
        .workout-banner {
            background:linear-gradient(135deg,#0e7490,#0891b2);
            color:white; padding:18px 24px; border-radius:12px; margin-bottom:20px;
        }
        .workout-banner h3 { margin:0 0 4px 0; font-size:1.1rem; font-weight:700; }
        .workout-banner p  { margin:0; font-size:0.9rem; opacity:0.85; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            height:100%; display:flex; flex-direction:column; justify-content:space-between;
        }
        </style>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="AI Fitness Tracker", page_icon="💪", layout="wide")
inject_css()


@st.cache_data
def get_data():
    df_users, df_logs = load_data()
    df_users["equipment"]          = df_users["equipment"].apply(ast.literal_eval)
    df_users["preferred_workouts"] = df_users["preferred_workouts"].apply(ast.literal_eval)
    return df_users, df_logs

df_users, df_logs = get_data()


# Sidebar

st.sidebar.title("💪 AI Fitness Tracker")
st.sidebar.divider()
page = st.sidebar.radio("Navigate", ["🌍 Global Dashboard", "👤 User Dashboard"])

if page == "👤 User Dashboard":
    user_num = st.sidebar.number_input("Enter user number (1–500)", min_value=1, max_value=500, value=1)
    user_id  = f"u_{user_num:04d}"
    try:
        sb = user_summary(user_id, df_users, df_logs)
        st.sidebar.divider()
        st.sidebar.markdown(f"**{sb['name']}**")
        st.sidebar.caption(f"🎯 {sb['goal'].replace('_',' ').title()}")
        st.sidebar.caption(f"⚡ {sb['fitness_level'].title()}")
        st.sidebar.caption(f"📅 {sb['total_days_logged']} days logged")
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
    with col_left:  st.pyplot(cached_plot_global_calories())
    with col_right: st.pyplot(cached_plot_global_freq())


# User Dashboard

elif page == "👤 User Dashboard":
    stats     = user_summary(user_id, df_users, df_logs)
    user_logs = df_logs[df_logs["user_id"] == user_id]
    recent    = get_last_7_days(user_id, df_logs)
    injuries  = get_user_injuries(user_id)

    st.title(f"👤 {stats['name']}")
    st.caption(f"User {user_id}  ·  {stats['goal'].replace('_',' ').title()}  ·  {stats['fitness_level'].title()}")
    st.divider()

    st.subheader("Profile")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎂 Age",           stats["age"])
    col2.metric("🎯 Goal",          stats["goal"].replace("_"," ").title())
    col3.metric("⚡ Fitness Level", stats["fitness_level"].title())
    col4.metric("📅 Days Logged",   stats["total_days_logged"])

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**🏋️ Equipment**")
        st.write(", ".join([e.replace("_"," ").title() for e in stats["equipment"]]))
    with col_right:
        st.markdown("**❤️ Preferred Workouts**")
        st.write(", ".join(stats["preferred_workouts"]))

    if injuries:
        st.warning("⚠️ This user has recorded injuries — the workout generator will account for these.")
        for inj in injuries:
            st.caption(f"🩹 **{inj['body_part'].replace('_',' ').title()}** — {inj['severity'].replace('_',' ').title()}: {inj['notes']}")

    st.divider()

    st.subheader("📊 Activity Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚶 Avg Daily Steps",      f"{stats['avg_daily_steps']:,}")
    col2.metric("🔥 Avg Daily Calories",   f"{stats['avg_daily_calories']} kcal")
    col3.metric("⏱️ Avg Workout Duration", f"{stats['avg_workout_duration']} min")
    col4.metric("🏆 Favourite Workout",    stats["favourite_workout"])
    st.divider()

    st.subheader("📈 Progress Over Time")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1: st.pyplot(cached_plot_steps(user_id, stats["name"]))
    with chart_col2: st.pyplot(cached_plot_calories(user_id, stats["name"]))
    freq_left, freq_mid, freq_right = st.columns([1, 2, 1])
    with freq_mid: st.pyplot(cached_plot_freq(user_id, stats["name"]))
    st.divider()

    st.subheader("⚡ Today's Workout")

    # Session state — all list updates use reassignment to avoid Streamlit mutation detection issues
    for key, default in [
        ("workout",            None),
        ("rejected",           []),
        ("all_rejected",       []),
        ("all_liked",          []),
        ("pinned",             []),
        ("selected_saved",     None),
        ("pool",               None),
        ("pool_selected",      []),
        ("pool_sets",          {}),
        ("pool_reps",          {}),
        ("filter_version",     0),
        ("last_pool_muscles",  []),
        ("last_pool_equipment",[]),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


    # Saved workouts
    saved = get_user_saved_workouts(user_id)
    if saved:
        with st.expander(f"💾  {len(saved)} saved workout(s) — click to browse"):
            st.caption("Your previously saved workouts. Select one to load it.")
            st.divider()
            card_cols = st.columns(3)
            for i, w in enumerate(saved):
                with card_cols[i % 3]:
                    st.markdown(f"""
                        <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);color:white;
                                    padding:14px 16px;border-radius:10px;margin-bottom:6px;">
                            <div style="font-size:0.65rem;letter-spacing:1px;opacity:0.6;margin-bottom:6px">WORKOUT {i+1}</div>
                            <div style="font-size:0.82rem;font-weight:600;line-height:1.35;margin-bottom:8px">{truncate(w['workout_summary'],65)}</div>
                            <div style="font-size:0.72rem;opacity:0.65">{len(w['exercises'])} exercises</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Load workout →", key=f"load_{i}", use_container_width=True):
                        st.session_state.selected_saved = i

            if st.session_state.selected_saved is not None:
                sel = saved[st.session_state.selected_saved]
                st.divider()
                st.markdown(f"""
                    <div class="workout-banner">
                        <h3>💾 {sel['workout_summary']}</h3>
                        <p>Saved workout {st.session_state.selected_saved + 1}</p>
                    </div>
                """, unsafe_allow_html=True)
                map_col, cards_col = st.columns([1, 3])
                with map_col:
                    st.pyplot(plot_muscle_map(sel["exercises"], MUSCLE_COLORS))
                with cards_col:
                    cols = st.columns(3)
                    for i, ex in enumerate(sel["exercises"]):
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
                                st.caption(f"🏋️ {ex['equipment'].replace('_',' ').title()}")
                                st.caption(f"💡 {truncate(ex['notes'])}")


    # Build Your Own — no st.form, plain buttons only for reliable state management
    with st.expander("🔨 Build Your Own Workout"):
        st.caption("Set filters, generate suggestions, add exercises to your selection, adjust sets and reps, then build.")

        # Filters — plain multiselects, no form
        # Changes cause harmless reruns; nothing happens until Generate is clicked
        fc1, fc2 = st.columns(2)
        with fc1:
            pool_muscles = st.multiselect(
                "Target muscle groups",
                options=["chest","back","legs","shoulders","arms","core","cardio"],
                default=st.session_state.last_pool_muscles,
                key=f"pool_muscles_{st.session_state.filter_version}"
            )
        with fc2:
            pool_equipment = st.multiselect(
                "Equipment",
                options=["bodyweight","dumbbells","barbells","full_gym",
                         "resistance_bands","kettlebells","elliptical","treadmill","rowing_machine"],
                default=st.session_state.last_pool_equipment or list(stats["equipment"]),
                key=f"pool_equipment_{st.session_state.filter_version}"
            )

        btn1, btn2, btn3 = st.columns([3, 1, 1])
        with btn1:
            if st.button("⚡ Generate Suggestions", type="primary", use_container_width=True, key="gen_pool"):
                st.session_state.last_pool_muscles   = list(pool_muscles)
                st.session_state.last_pool_equipment = list(pool_equipment)
                with st.spinner("Generating exercise pool..."):
                    # Pool refreshes; pool_selected is intentionally preserved
                    st.session_state.pool = generate_exercise_pool(stats, pool_muscles, pool_equipment)

        with btn2:
            if st.button("＋ More", use_container_width=True, key="more_pool",
                         disabled=not bool(st.session_state.pool)):
                st.session_state.last_pool_muscles   = list(pool_muscles)
                st.session_state.last_pool_equipment = list(pool_equipment)
                with st.spinner("Fetching more..."):
                    more_pool      = generate_exercise_pool(stats, pool_muscles, pool_equipment, 6)
                    existing_names = {ex["name"] for ex in st.session_state.pool}
                    new_ones       = [ex for ex in more_pool if ex["name"] not in existing_names]
                    st.session_state.pool = st.session_state.pool + new_ones

        with btn3:
            if st.button("🔄 Clear", use_container_width=True, key="clear_filters_btn"):
                st.session_state.last_pool_muscles   = []
                st.session_state.last_pool_equipment = list(stats["equipment"])
                st.session_state.filter_version     += 1

        # Your Selections — persists across pool regenerations and filter changes
        sel_count   = len(st.session_state.pool_selected)
        pool_lookup = {ex["name"]: ex for ex in (st.session_state.pool or [])}

        if sel_count > 0:
            st.divider()
            hdr_col, clr_col = st.columns([4, 1])
            with hdr_col:
                st.markdown(f"**📋 Your selections ({sel_count} exercises)**")
            with clr_col:
                if st.button("Clear All", key="clear_all_sel"):
                    st.session_state.pool_selected = []
                    st.session_state.pool_sets     = {}
                    st.session_state.pool_reps     = {}

            for ex_name in list(st.session_state.pool_selected):
                ex_data = pool_lookup.get(ex_name, {"sets":3,"reps":10,"muscle_group":"varied"})
                color   = MUSCLE_COLORS.get(ex_data.get("muscle_group","").lower(), ACCENT)

                row_name, row_sets, row_reps, row_del = st.columns([4, 1, 1, 1])
                with row_name:
                    st.markdown(f"""
                        <div style="background:{hex_lighten(color,0.88)};border-left:4px solid {color};
                                    padding:8px 12px;border-radius:4px;font-size:0.85rem;
                                    font-weight:600;color:#1e293b;margin-bottom:4px;">{ex_name}</div>
                    """, unsafe_allow_html=True)
                with row_sets:
                    sets_val = st.session_state.pool_sets.get(ex_name, ex_data.get("sets", 3))
                    sets_val = max(1, min(10, int(sets_val)))  # clamp to widget range
                    sv = st.number_input("Sets", 1, 10, value=sets_val, key=f"sel_sets_{ex_name}")
                    st.session_state.pool_sets = {**st.session_state.pool_sets, ex_name: sv}
                with row_reps:
                    reps_val = st.session_state.pool_reps.get(ex_name, ex_data.get("reps", 10))
                    reps_val = max(1, min(50, int(reps_val)))  # clamp LLM values to widget range
                    rv = st.number_input("Reps", 1, 50, value=reps_val, key=f"sel_reps_{ex_name}")
                    st.session_state.pool_reps = {**st.session_state.pool_reps, ex_name: rv}
                with row_del:
                    if st.button("✕", key=f"remove_sel_{ex_name}"):
                        st.session_state.pool_selected = [x for x in st.session_state.pool_selected if x != ex_name]

            st.divider()
            workout_name_input = st.text_input(
                "Give your workout a name",
                placeholder="e.g. Upper body push, Leg day, Active recovery...",
                key="custom_workout_name"
            )

            b_left, b_mid, b_right = st.columns([1, 2, 1])
            with b_mid:
                if st.button(f"🏋️ Build Workout  ({sel_count} exercises)", type="primary", use_container_width=True):
                    selected_exercises = []
                    for ex_name in st.session_state.pool_selected:
                        ex_data         = pool_lookup.get(ex_name, {
                            "name":ex_name,"sets":3,"reps":10,
                            "muscle_group":"varied","equipment":"bodyweight","notes":"User-selected exercise."
                        })
                        ex_copy         = ex_data.copy()
                        ex_copy["name"] = ex_name
                        ex_copy["sets"] = st.session_state.pool_sets.get(ex_name, ex_data.get("sets",3))
                        ex_copy["reps"] = st.session_state.pool_reps.get(ex_name, ex_data.get("reps",10))
                        selected_exercises.append(ex_copy)

                    summary = workout_name_input.strip() if workout_name_input.strip() else f"Custom workout — {sel_count} exercises"
                    st.session_state.workout       = {"workout_summary": summary, "exercises": selected_exercises}
                    st.session_state.rejected      = []
                    st.session_state.all_rejected  = []
                    st.session_state.all_liked     = []
                    st.session_state.pool          = None
                    st.session_state.pool_selected = []
                    st.session_state.pool_sets     = {}
                    st.session_state.pool_reps     = {}
                    st.rerun()

        # Exercise pool — browse and add
        if st.session_state.pool:
            st.divider()
            st.caption(f"**Exercise pool** — {len(st.session_state.pool)} suggestions · click to add to your selection")

            pool_cols = st.columns(3)
            for i, ex in enumerate(st.session_state.pool):
                is_sel       = ex["name"] in st.session_state.pool_selected
                color        = MUSCLE_COLORS.get(ex["muscle_group"].lower(), ACCENT)
                header_color = color if is_sel else "#94a3b8"

                with pool_cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"""
                            <div class="exercise-card-header" style="background:{header_color}">
                                <p class="exercise-name">{'✅ ' if is_sel else ''}{ex['name']}</p>
                                <span class="muscle-badge">{ex['muscle_group']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.caption(f"🏋️ {ex['equipment'].replace('_',' ').title()}")
                        st.caption(f"💡 {truncate(ex['notes'])}")

                        if is_sel:
                            if st.button("✅ Added", key=f"sel_on_{ex['name']}", use_container_width=True):
                                st.session_state.pool_selected = [x for x in st.session_state.pool_selected if x != ex["name"]]
                                st.rerun()
                        else:
                            if st.button("＋ Add", key=f"sel_off_{ex['name']}", use_container_width=True):
                                st.session_state.pool_selected = st.session_state.pool_selected + [ex["name"]]
                                st.rerun()


    # Liked exercises
    liked_history = get_user_liked_exercises(user_id)
    if liked_history:
        pinned_count   = len(st.session_state.pinned)
        expander_label = (
            f"❤️  {len(liked_history)} liked exercise(s)  ·  {pinned_count} pinned"
            if pinned_count > 0
            else f"❤️  {len(liked_history)} liked exercise(s)  ·  pin to include in next workout"
        )
        with st.expander(expander_label):
            if pinned_count >= 4:
                st.info("📌 **4 exercises pinned.** Great — train what you love. Remember: the best results come from a balanced plan. The AI will build around your picks.")
            else:
                st.caption(f"Pin up to 4 exercises to guarantee them in your next workout. {4-pinned_count} slot(s) remaining.")

            cols = st.columns(4)
            for i, ex_name in enumerate(liked_history):
                is_pinned = ex_name in st.session_state.pinned
                color     = PILL_COLORS[i % len(PILL_COLORS)]
                light_bg  = hex_lighten(color)
                bg, border, text, icon = (color,color,"white","📌 ") if is_pinned else (light_bg,color,color,"")

                with cols[i % 4]:
                    st.markdown(f"""
                        <div style="background:{bg};border:2px solid {border};color:{text};
                                    padding:8px 10px;border-radius:8px;font-size:0.75rem;font-weight:700;
                                    text-align:center;min-height:44px;display:flex;
                                    align-items:center;justify-content:center;margin-bottom:4px;">{icon}{ex_name}</div>
                    """, unsafe_allow_html=True)

                    if is_pinned:
                        if st.button("Unpin", key=f"pin_{ex_name}", use_container_width=True):
                            st.session_state.pinned = [x for x in st.session_state.pinned if x != ex_name]
                    elif pinned_count < 4:
                        if st.button("Pin", key=f"pin_{ex_name}", use_container_width=True):
                            st.session_state.pinned = st.session_state.pinned + [ex_name]
                    else:
                        st.button("Pin", key=f"pin_{ex_name}", disabled=True, use_container_width=True)

    # Disliked exercises
    disliked = stats.get("disliked_exercises", [])
    if isinstance(disliked, str):
        disliked = ast.literal_eval(disliked)
    if disliked:
        with st.expander(f"🚫  {len(disliked)} disliked exercise(s)"):
            st.write(", ".join(disliked))

    # Generate button
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        if st.button("⚡ Generate Today's Workout Using your AI trainer", type="primary", use_container_width=True):
            with st.spinner("Building your personalised workout..."):
                st.session_state.workout        = generate_workout(
                    stats, recent,
                    pinned_exercises=st.session_state.pinned if st.session_state.pinned else None
                )
                st.session_state.rejected       = []
                st.session_state.all_rejected   = []
                st.session_state.all_liked      = []
                st.session_state.pinned         = []
                st.session_state.selected_saved = None

    if st.session_state.workout:
        workout       = st.session_state.workout
        num_exercises = len(workout["exercises"])

        st.markdown(f"""
            <div class="workout-banner">
                <h3>🏋️ {workout['workout_summary']}</h3>
                <p>{num_exercises} exercises  ·  ~{num_exercises*10} min estimated</p>
            </div>
        """, unsafe_allow_html=True)

        map_col, cards_col = st.columns([1, 3])
        with map_col:
            st.pyplot(plot_muscle_map(workout["exercises"], MUSCLE_COLORS))

        with cards_col:
            cols = st.columns(3)
            for i, ex in enumerate(workout["exercises"]):
                is_rejected = ex["name"] in st.session_state.rejected
                is_liked    = ex["name"] in st.session_state.all_liked
                color       = MUSCLE_COLORS.get(ex["muscle_group"].lower(), ACCENT)

                with cols[i % 3]:
                    with st.container(border=True):
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
                        st.caption(f"🏋️ {ex['equipment'].replace('_',' ').title()}")
                        st.caption(f"💡 {truncate(ex['notes'])}")

                        if is_rejected:
                            if st.button("↩️ Undo", key=f"undo_{ex['name']}", use_container_width=True):
                                st.session_state.rejected     = [x for x in st.session_state.rejected if x != ex["name"]]
                                st.session_state.all_rejected = [x for x in st.session_state.all_rejected if x != ex["name"]]
                                st.rerun()
                        else:
                            heart_label = "❤️ Liked" if is_liked else "🤍 Like"
                            if st.button(heart_label, key=f"like_{ex['name']}", use_container_width=True):
                                if is_liked:
                                    st.session_state.all_liked = [x for x in st.session_state.all_liked if x != ex["name"]]
                                else:
                                    st.session_state.all_liked = st.session_state.all_liked + [ex["name"]]
                                st.rerun()
                            if st.button("👎 Reject", key=f"reject_{ex['name']}", use_container_width=True):
                                if ex["name"] not in st.session_state.rejected:
                                    st.session_state.rejected     = st.session_state.rejected + [ex["name"]]
                                    st.session_state.all_rejected = st.session_state.all_rejected + [ex["name"]]
                                st.rerun()

        st.divider()
        col_left, col_mid, col_right = st.columns([1, 2, 1])
        with col_mid:
            if st.session_state.rejected:
                if st.button("🔄 Regenerate Rejected", type="primary", use_container_width=True):
                    with st.spinner("Swapping out exercises..."):
                        st.session_state.workout  = generate_workout(
                            stats, recent, st.session_state.rejected, st.session_state.workout
                        )
                        st.session_state.rejected = []
                        st.rerun()

            if st.button("💾 Save Workout", type="primary", use_container_width=True):
                save_workout(user_id, workout, st.session_state.all_rejected, st.session_state.all_liked)
                st.session_state.all_rejected = []
                st.session_state.all_liked    = []
                st.success("Workout saved! Your feedback has been recorded. 🎉")