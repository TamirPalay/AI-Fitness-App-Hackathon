"""
generate_users.py
-----------------
Generates a JSON file of 500 simulated user profiles,
each with personal attributes, equipment, injuries, and
30-60 days of daily activity logs.

Run from the project root:
    python src/generate_users.py
Output: data/raw/users.json
"""

import json
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
random.seed(42)


# Constants

GOALS = ["weight_loss", "strength", "cardio", "flexibility", "general_fitness", "rehabilitation"]
FITNESS_LEVELS = ["beginner", "intermediate", "advanced"]

EQUIPMENT_OPTIONS = ["bodyweight", "dumbbells", "barbells", "full_gym", "resistance_bands", "kettlebells", "elliptical", "treadmill", "rowing_machine"]

BODY_PARTS = [
    "left_knee", "right_knee",
    "left_shoulder", "right_shoulder",
    "left_wrist", "right_wrist",
    "lower_back", "upper_back",
    "left_ankle", "right_ankle",
    "neck"
]

INJURY_SEVERITIES = ["immobile", "in_recovery", "sensitive"]

INJURY_NOTES = {
    "immobile":    "No movement or load on this area.",
    "in_recovery": "Light exercises only, avoid strain.",
    "sensitive":   "Recovered but monitor for discomfort."
}

WORKOUT_TYPES = ["Yoga", "HIIT", "Running", "Strength", "Cycling", "Swimming", "Rest"]


# Helper functions

def generate_equipment():
    equipment = ["bodyweight"]
    candidates = [opt for opt in EQUIPMENT_OPTIONS if opt != "bodyweight"]
    for item in candidates:
        if random.random() < 0.3:
            equipment.append(item)
    return equipment


def generate_injuries():
    if random.random() < 0.70:
        return []

    num_injuries = random.randint(1, 2)
    injured_parts = random.sample(BODY_PARTS, num_injuries)

    injuries = []
    for part in injured_parts:
        severity = random.choice(INJURY_SEVERITIES)
        injuries.append({
            "body_part": part,
            "severity": severity,
            "notes": INJURY_NOTES[severity]
        })
    return injuries


def generate_daily_logs(num_days: int, fitness_level: str) -> list:
    base_steps = {"beginner": 4000, "intermediate": 7000, "advanced": 10000}
    base_calories = {"beginner": 200, "intermediate": 350, "advanced": 500}

    logs = []
    start_date = date.today() - timedelta(days=num_days)

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        workout = random.choice(WORKOUT_TYPES)

        if workout == "Rest":
            steps = random.randint(500, 2000)
            calories = random.randint(50, 150)
            duration = 0
        else:
            steps = max(500, int(random.gauss(base_steps[fitness_level], 1500)))
            calories = max(50, int(random.gauss(base_calories[fitness_level], 80)))
            duration = random.randint(20, 75)

        logs.append({
            "date": str(current_date),
            "steps": steps,
            "calories_burned": calories,
            "workout_type": workout,
            "duration_minutes": duration,
            "workout_rating": random.randint(1, 5)
        })

    return logs


def generate_user(user_id: int) -> dict:
    fitness_level = random.choice(FITNESS_LEVELS)
    num_days = random.randint(30, 60)

    return {
        "user_id": f"u_{user_id:04d}",
        "name": fake.name(),
        "age": random.randint(18, 65),
        "weight_kg": round(random.uniform(50, 120), 1),
        "height_cm": random.randint(155, 195),
        "goal": random.choice(GOALS),
        "fitness_level": fitness_level,
        "equipment": generate_equipment(),
        "injuries": generate_injuries(),
        "daily_logs": generate_daily_logs(num_days, fitness_level)
    }


# Main

def main():
    num_users = 500
    print(f"Generating {num_users} users...")

    users = [generate_user(i) for i in range(1, num_users + 1)]

    output_path = "data/raw/users.json"
    with open(output_path, "w") as f:
        json.dump(users, f, indent=2)

    print(f"Done. Saved to {output_path}")
    print(f"Total users: {len(users)}")
    print(f"Sample user: {users[0]['name']}, goal: {users[0]['goal']}, equipment: {users[0]['equipment']}")


if __name__ == "__main__":
    main()