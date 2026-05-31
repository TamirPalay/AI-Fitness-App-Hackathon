"""
statistics.py
-------------
SciPy statistical analyses for the fitness tracker.

1. ANOVA:          Do calories burned differ significantly across workout types?
2. Linear regression: Predict future steps based on past trends.
3. Paired t-test:  Do users rate high-intensity workouts differently than low-intensity?

Run from the project root:
    python src/statistics.py
"""

import numpy as np
import pandas as pd
from scipy import stats


# 1. ANOVA — calories burned across workout types

def anova_calories_by_workout(df_logs: pd.DataFrame) -> dict:
    active = df_logs[df_logs["workout_type"] != "Rest"]

    # Build a list of calorie arrays, one per workout type
    groups = [
        group["calories_burned"].values
        for _, group in active.groupby("workout_type")
    ]

    f_stat, p_value = stats.f_oneway(*groups)

    return {
        "f_statistic": round(f_stat, 4),
        "p_value":     round(p_value, 6),
        "significant": p_value < 0.05,
        "conclusion":  (
            "Calorie burn differs significantly across workout types."
            if p_value < 0.05
            else "No significant difference in calorie burn across workout types."
        )
    }


# 2. Linear regression — predict steps trend for a user

def regression_steps_trend(user_logs: pd.DataFrame) -> dict:
    df = user_logs.sort_values("date").copy()

    # Convert dates to numeric (days since first log)
    df["day_num"] = (df["date"] - df["date"].min()).dt.days

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df["day_num"], df["steps"]
    )

    # Predict steps for next 7 days
    last_day = df["day_num"].max()
    future_days = np.array([last_day + i for i in range(1, 8)])
    predicted_steps = list(map(lambda d: round(slope * d + intercept), future_days))

    return {
        "slope":           round(slope, 2),
        "r_squared":       round(r_value ** 2, 4),
        "p_value":         round(p_value, 6),
        "trend":           "improving" if slope > 0 else "declining",
        "predicted_steps": predicted_steps
    }


# 3. Paired t-test — high intensity vs low intensity workout ratings

def ttest_workout_intensity_ratings(df_logs: pd.DataFrame) -> dict:
    high_intensity = ["HIIT", "Running"]
    low_intensity  = ["Yoga", "Swimming"]

    high = df_logs[df_logs["workout_type"].isin(high_intensity)]["workout_rating"]
    low  = df_logs[df_logs["workout_type"].isin(low_intensity)]["workout_rating"]

    # Sample equal sizes for a valid paired t-test
    min_size = min(len(high), len(low))
    high_sample = high.sample(min_size, random_state=42).values
    low_sample  = low.sample(min_size, random_state=42).values

    t_stat, p_value = stats.ttest_rel(high_sample, low_sample)

    return {
        "t_statistic":    round(t_stat, 4),
        "p_value":        round(p_value, 6),
        "significant":    p_value < 0.05,
        "high_intensity_avg": round(high.mean(), 2),
        "low_intensity_avg":  round(low.mean(), 2),
        "conclusion": (
            "Users rate high and low intensity workouts significantly differently."
            if p_value < 0.05
            else "No significant difference in ratings between high and low intensity workouts."
        )
    }


# Main

if __name__ == "__main__":
    from analysis import load_data

    df_users, df_logs = load_data()
    user_logs = df_logs[df_logs["user_id"] == "u_0001"]

    print("-- ANOVA: Calories by Workout Type --")
    anova = anova_calories_by_workout(df_logs)
    for k, v in anova.items():
        print(f"  {k}: {v}")

    print("\n-- Linear Regression: Steps Trend (u_0001) --")
    regression = regression_steps_trend(user_logs)
    for k, v in regression.items():
        print(f"  {k}: {v}")

    print("\n-- Paired T-Test: High vs Low Intensity Ratings --")
    ttest = ttest_workout_intensity_ratings(df_logs)
    for k, v in ttest.items():
        print(f"  {k}: {v}")