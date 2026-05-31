"""
workout_generator.py
--------------------
Handles LLM workout generation via Groq and saved workout management.

"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Saved workouts helpers

SAVED_WORKOUTS_PATH = "data/raw/saved_workouts.json"


def load_saved_workouts() -> dict:
    if not os.path.exists(SAVED_WORKOUTS_PATH):
        return {}
    with open(SAVED_WORKOUTS_PATH, "r") as f:
        return json.load(f)


def save_workout(user_id: str, workout: dict):
    saved = load_saved_workouts()
    if user_id not in saved:
        saved[user_id] = []
    saved[user_id].append(workout)
    with open(SAVED_WORKOUTS_PATH, "w") as f:
        json.dump(saved, f, indent=2)


def get_user_saved_workouts(user_id: str) -> list:
    saved = load_saved_workouts()
    return saved.get(user_id, [])


# Prompt builder

def build_prompt(user_stats: dict, last_7_days, rejected_exercises: list = None) -> str:
    # Summarise last 7 days
    recent = []
    for _, row in last_7_days.iterrows():
        recent.append(f"  {row['date'].date()}: {row['workout_type']}, "
                      f"{row['steps']} steps, {row['calories_burned']} kcal, "
                      f"rating {row['workout_rating']}/5")
    recent_str = "\n".join(recent)

    # Build rejection instruction if needed
    rejection_str = ""
    if rejected_exercises:
        rejection_str = f"""
The user rejected these exercises, replace them with alternatives:
{', '.join(rejected_exercises)}
"""

    prompt = f"""
You are a personal fitness coach. Generate a workout plan for today based on the following user profile.

User Profile:
- Goal: {user_stats['goal']}
- Fitness level: {user_stats['fitness_level']}
- Available equipment: {', '.join(user_stats['equipment'])}
- Preferred workouts: {', '.join(user_stats['preferred_workouts'])}
- Has injuries: {user_stats['has_injuries']}

Last 7 days of activity:
{recent_str}

{rejection_str}

Rules:
- Only use the equipment listed above
- If the user has injuries, avoid exercises that stress injured areas
- Take into account recent activity — if they trained hard yesterday, suggest lighter work today
- Suggest 4 to 6 exercises

Respond ONLY with a JSON object in this exact format, no extra text:
{{
  "workout_summary": "brief description of today's workout",
  "exercises": [
    {{
      "name": "exercise name",
      "sets": 3,
      "reps": 10,
      "equipment": "equipment used",
      "muscle_group": "primary muscle group",
      "notes": "short coaching tip"
    }}
  ]
}}
"""
    return prompt


# LLM call

def generate_workout(user_stats: dict, last_7_days, rejected_exercises: list = None) -> dict:
    prompt = build_prompt(user_stats, last_7_days, rejected_exercises)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)

if __name__ == "__main__":
    from analysis import load_data, user_summary, last_7_days

    df_users, df_logs = load_data()
    stats = user_summary("u_0001", df_users, df_logs)
    recent = last_7_days("u_0001", df_logs)

    print("Generating workout...")
    workout = generate_workout(stats, recent)
    print(json.dumps(workout, indent=2))