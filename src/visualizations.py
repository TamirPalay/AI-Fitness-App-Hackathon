"""
visualizations.py
-----------------
All chart functions for the fitness tracker.
Each function can run standalone or be called from the Streamlit dashboard.

Run from the project root to test:
    python src/visualizations.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")


# Global charts

def plot_calories_by_workout(df_logs: pd.DataFrame):
    active = df_logs[df_logs["workout_type"] != "Rest"]
    avg_calories = (
        active.groupby("workout_type")["calories_burned"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=avg_calories, x="workout_type", y="calories_burned", ax=ax, palette="muted")
    ax.set_title("Average Calories Burned by Workout Type")
    ax.set_xlabel("Workout Type")
    ax.set_ylabel("Avg Calories Burned")
    plt.tight_layout()
    return fig


def plot_workout_frequency(df_logs: pd.DataFrame):
    active = df_logs[df_logs["workout_type"] != "Rest"]
    counts = active["workout_type"].value_counts().reset_index()
    counts.columns = ["workout_type", "count"]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=counts, x="workout_type", y="count", ax=ax, palette="muted")
    ax.set_title("Workout Frequency Across All Users")
    ax.set_xlabel("Workout Type")
    ax.set_ylabel("Total Sessions")
    plt.tight_layout()
    return fig


# User specific charts

def plot_steps_over_time(df_logs: pd.DataFrame, user_name: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_logs, x="date", y="steps", ax=ax, color="steelblue")
    ax.set_title(f"Daily Steps Over Time — {user_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Steps")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_calories_over_time(df_logs: pd.DataFrame, user_name: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_logs, x="date", y="calories_burned", ax=ax, color="coral")
    ax.set_title(f"Calories Burned Over Time — {user_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories Burned")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_user_workout_frequency(df_logs: pd.DataFrame, user_name: str):
    active = df_logs[df_logs["workout_type"] != "Rest"]
    counts = active["workout_type"].value_counts().reset_index()
    counts.columns = ["workout_type", "count"]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=counts, x="workout_type", y="count", ax=ax, palette="muted")
    ax.set_title(f"Workout Frequency — {user_name}")
    ax.set_xlabel("Workout Type")
    ax.set_ylabel("Sessions")
    plt.tight_layout()
    return fig


# Test

if __name__ == "__main__":
    from analysis import load_data

    df_users, df_logs = load_data()
    user_logs = df_logs[df_logs["user_id"] == "u_0001"]

    plot_calories_by_workout(df_logs)
    plot_workout_frequency(df_logs)
    plot_steps_over_time(user_logs, "Thomas Brown")
    plot_calories_over_time(user_logs, "Thomas Brown")
    plot_user_workout_frequency(user_logs, "Thomas Brown")

    plt.show()