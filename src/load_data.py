"""
load_data.py
------------
Loads users.json and produces two flat DataFrames:
  - df_users: one row per user (profile attributes)
  - df_logs:  one row per daily log entry (linked by user_id)

Run from the project root:
    python src/load_data.py
Output:
    data/processed/users.csv
    data/processed/logs.csv
"""

import json
import pandas as pd


def load_json(path: str) -> list:
    with open(path, "r") as f:
        return json.load(f)


def build_users_df(users: list) -> pd.DataFrame:
    # Drop nested fields — they belong in their own DataFrames
    rows = []
    for user in users:
        rows.append({
            "user_id":       user["user_id"],
            "name":          user["name"],
            "age":           user["age"],
            "weight_kg":     user["weight_kg"],
            "height_cm":     user["height_cm"],
            "goal":          user["goal"],
            "fitness_level": user["fitness_level"],
            "equipment":     user["equipment"],  # kept as list for now
            "has_injuries":  len(user["injuries"]) > 0,
            "injury_count":  len(user["injuries"]),
            "preferred_workouts": user["preferred_workouts"],
            "disliked_exercises": user["disliked_exercises"]
        })
    return pd.DataFrame(rows)


def build_logs_df(users: list) -> pd.DataFrame:
    rows = []
    for user in users:
        for log in user["daily_logs"]:
            rows.append({
                "user_id":          user["user_id"],
                "date":             pd.to_datetime(log["date"]),
                "steps":            log["steps"],
                "calories_burned":  log["calories_burned"],
                "workout_type":     log["workout_type"],
                "duration_minutes": log["duration_minutes"],
                "workout_rating":   log["workout_rating"]
            })
    return pd.DataFrame(rows)


def validate(df_users: pd.DataFrame, df_logs: pd.DataFrame):
    print("-- Users DataFrame --")
    print(f"  Shape:   {df_users.shape}")
    print(f"  Nulls:\n{df_users.isnull().sum()}")

    print("\n-- Logs DataFrame --")
    print(f"  Shape:   {df_logs.shape}")
    print(f"  Nulls:\n{df_logs.isnull().sum()}")
    print(f"  Date range: {df_logs['date'].min()} -> {df_logs['date'].max()}")
    print(f"  Workout types: {sorted(df_logs['workout_type'].unique())}")


def main():
    users = load_json("data/raw/users.json")

    df_users = build_users_df(users)
    df_logs  = build_logs_df(users)

    validate(df_users, df_logs)

    df_users.to_csv("data/processed/users.csv", index=False)
    df_logs.to_csv("data/processed/logs.csv",   index=False)
    print("\nSaved to data/processed/")


if __name__ == "__main__":
    main()