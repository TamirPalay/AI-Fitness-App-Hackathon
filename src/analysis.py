"""
analysis.py
-----------
Loads the processed CSVs and performs exploratory data analysis.

Run from the project root:
    python src/analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Load data

def load_data():
    df_users = pd.read_csv("data/processed/users.csv")
    df_logs  = pd.read_csv("data/processed/logs.csv", parse_dates=["date"])
    return df_users, df_logs

# Weekly aggregations

def weekly_summary(df_logs: pd.DataFrame) -> pd.DataFrame:
    df = df_logs.copy()
    df["week"] = df["date"].dt.to_period("W")

    weekly = (
        df.groupby(["user_id", "week"])
        .agg(
            total_steps        = ("steps",            "sum"),
            total_calories     = ("calories_burned",  "sum"),
            total_workouts     = ("workout_type",     lambda x: (x != "Rest").sum()),
            rest_days          = ("workout_type",     lambda x: (x == "Rest").sum()),
            avg_workout_rating = ("workout_rating",   "mean")
        )
        .reset_index()
    )
    return weekly

# Global summary stats

def global_summary(df_logs: pd.DataFrame) -> dict:
    active = df_logs[df_logs["workout_type"] != "Rest"]

    return {
        "avg_daily_steps":       round(df_logs["steps"].mean()),
        "avg_daily_calories":    round(df_logs["calories_burned"].mean()),
        "avg_workout_duration":  round(active["duration_minutes"].mean(), 1),
        "most_popular_workout":  active["workout_type"].value_counts().idxmax(),
        "avg_workout_rating":    round(df_logs["workout_rating"].mean(), 2),
        "total_rest_day_pct":    round((df_logs["workout_type"] == "Rest").mean() * 100, 1)
    }

# User specific stats

def user_summary(user_id: str, df_users: pd.DataFrame, df_logs: pd.DataFrame) -> dict:
    user   = df_users[df_users["user_id"] == user_id].iloc[0]
    logs   = df_logs[df_logs["user_id"] == user_id]
    active = logs[logs["workout_type"] != "Rest"]

    return {
        "name":                  user["name"],
        "age":                   user["age"],
        "goal":                  user["goal"],
        "fitness_level":         user["fitness_level"],
        "equipment":             user["equipment"],
        "has_injuries":          user["has_injuries"],
        "preferred_workouts":    user["preferred_workouts"],
        "avg_daily_steps":       round(logs["steps"].mean()),
        "avg_daily_calories":    round(logs["calories_burned"].mean()),
        "avg_workout_duration":  round(active["duration_minutes"].mean(), 1),
        "favourite_workout":     active["workout_type"].value_counts().idxmax(),
        "avg_workout_rating":    round(logs["workout_rating"].mean(), 2),
        "total_days_logged":     len(logs),
        "total_rest_days":       (logs["workout_type"] == "Rest").sum()
    }

# Last 7 days of activity for a user

def last_7_days(user_id: str, df_logs: pd.DataFrame) -> pd.DataFrame:
    logs = df_logs[df_logs["user_id"] == user_id].copy()
    logs = logs.sort_values("date").tail(7)
    return logs
    
def main():
    df_users, df_logs = load_data()
    print(f"Users: {df_users.shape}, Logs: {df_logs.shape}")

    weekly = weekly_summary(df_logs)
    print(f"\nWeekly summary shape: {weekly.shape}")
    print(weekly.head(10))
    
    summary = global_summary(df_logs)
    print("\nGlobal Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    user_stats = user_summary("u_0001", df_users, df_logs)
    print("\nUser Summary:")
    for key, value in user_stats.items():
        print(f"  {key}: {value}")
    
    recent = last_7_days("u_0001", df_logs)
    print("\nLast 7 days:")
    print(recent[["date", "workout_type", "steps", "calories_burned", "workout_rating"]].to_string(index=False))
if __name__ == "__main__":
    main()