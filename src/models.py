"""
models.py
---------
Defines the User class which wraps a user profile and their logs,
exposing analysis methods as object attributes.
"""

import pandas as pd
from analysis import load_data, weekly_summary, user_summary, last_7_days


class User:
    def __init__(self, user_id: str, df_users: pd.DataFrame, df_logs: pd.DataFrame):
        self.user_id  = user_id
        self.df_users = df_users
        self.df_logs  = df_logs
        self.profile  = df_users[df_users["user_id"] == user_id].iloc[0]
        self.logs     = df_logs[df_logs["user_id"] == user_id].copy()

    # Profile attributes
    @property
    def name(self):            return self.profile["name"]
    @property
    def age(self):             return self.profile["age"]
    @property
    def goal(self):            return self.profile["goal"]
    @property
    def fitness_level(self):   return self.profile["fitness_level"]
    @property
    def equipment(self):       return self.profile["equipment"]
    @property
    def has_injuries(self):    return self.profile["has_injuries"]
    @property
    def preferred_workouts(self): return self.profile["preferred_workouts"]

    # Analysis methods
    def get_summary(self) -> dict:
        return user_summary(self.user_id, self.df_users, self.df_logs)

    def get_weekly_summary(self) -> pd.DataFrame:
        return weekly_summary(self.logs)

    def get_last_7_days(self) -> pd.DataFrame:
        return last_7_days(self.user_id, self.df_logs)

    def __repr__(self):
        return f"User({self.user_id} | {self.name} | {self.goal} | {self.fitness_level})"

if __name__ == "__main__":
    from analysis import load_data

    df_users, df_logs = load_data()
    user = User("u_0001", df_users, df_logs)

    print(user)
    print(f"\nGoal: {user.goal}")
    print(f"Equipment: {user.equipment}")
    print(f"\nSummary:\n{user.get_summary()}")
    print(f"\nLast 7 days:\n{user.get_last_7_days()}")