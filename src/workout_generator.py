"""
workout_generator.py
--------------------
Handles LLM workout generation via Groq and saved workout management.
"""

import os
import ast
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SAVED_WORKOUTS_PATH = "data/raw/saved_workouts.json"
USERS_PATH          = "data/raw/users.json"


# Saved workout helpers

def load_saved_workouts() -> dict:
    if not os.path.exists(SAVED_WORKOUTS_PATH):
        return {}
    with open(SAVED_WORKOUTS_PATH, "r") as f:
        return json.load(f)


def get_user_saved_workouts(user_id: str) -> list:
    return load_saved_workouts().get(user_id, [])


def get_user_injuries(user_id: str) -> list:
    with open(USERS_PATH, "r") as f:
        users = json.load(f)
    for user in users:
        if user["user_id"] == user_id:
            return user["injuries"]
    return []


def get_user_liked_exercises(user_id: str) -> list:
    with open(USERS_PATH, "r") as f:
        users = json.load(f)
    for user in users:
        if user["user_id"] == user_id:
            return user["liked_exercises"]
    return []


def save_workout(user_id: str, workout: dict, all_rejected: list, all_liked: list):
    # Append workout to saved_workouts.json
    saved = load_saved_workouts()
    if user_id not in saved:
        saved[user_id] = []
    saved[user_id].append(workout)
    with open(SAVED_WORKOUTS_PATH, "w") as f:
        json.dump(saved, f, indent=2)

    # Persist feedback to user profile
    with open(USERS_PATH, "r") as f:
        users = json.load(f)

    for user in users:
        if user["user_id"] == user_id:
            existing_disliked = user["disliked_exercises"]
            existing_liked    = user["liked_exercises"]
            new_dislikes      = [ex for ex in all_rejected if ex not in existing_disliked]
            new_likes         = [ex for ex in all_liked    if ex not in existing_liked]
            user["disliked_exercises"].extend(new_dislikes)
            user["liked_exercises"].extend(new_likes)
            break

    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)


# Prompt builders

def build_prompt(user_stats: dict, last_7_days) -> str:
    recent_lines = []
    for _, row in last_7_days.iterrows():
        recent_lines.append(
            f"  {row['date'].date()}: {row['workout_type']}, "
            f"{row['steps']} steps, {row['calories_burned']} kcal, "
            f"rating {row['workout_rating']}/5"
        )
    recent_str = "\n".join(recent_lines)

    disliked = user_stats.get("disliked_exercises", [])
    if isinstance(disliked, str):
        disliked = ast.literal_eval(disliked)
    disliked_str = (
        f"- Exercises this user has repeatedly disliked — do NOT include: {', '.join(disliked)}\n"
        if disliked else ""
    )

    liked = user_stats.get("liked_exercises", [])
    if isinstance(liked, str):
        liked = ast.literal_eval(liked)
    liked_str = (
        f"- Exercises this user enjoys — try to include similar ones: {', '.join(liked)}\n"
        if liked else ""
    )

    prompt = f"""
You are a personal fitness coach. Generate a workout plan for today based on the following user profile.

User Profile:
- Goal: {user_stats['goal']}
- Fitness level: {user_stats['fitness_level']}
- Available equipment: {', '.join(user_stats['equipment'])}
- Preferred workouts: {', '.join(user_stats['preferred_workouts'])}
- Has injuries: {user_stats['has_injuries']}
{disliked_str}{liked_str}
Last 7 days of activity:
{recent_str}

Rules:
- Only use the equipment listed above
- If the user has injuries, avoid exercises that stress injured areas
- Take into account recent activity — if they trained hard yesterday, suggest lighter work today
- Do not suggest any exercise the user has previously disliked
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


def build_prompt_with_pinned(user_stats: dict, last_7_days, pinned_names: list, num_to_generate: int) -> str:
    recent_lines = []
    for _, row in last_7_days.iterrows():
        recent_lines.append(
            f"  {row['date'].date()}: {row['workout_type']}, "
            f"{row['steps']} steps, {row['calories_burned']} kcal, "
            f"rating {row['workout_rating']}/5"
        )
    recent_str = "\n".join(recent_lines)

    disliked = user_stats.get("disliked_exercises", [])
    if isinstance(disliked, str):
        disliked = ast.literal_eval(disliked)
    disliked_str = (
        f"- Exercises this user dislikes — do NOT include: {', '.join(disliked)}\n"
        if disliked else ""
    )

    total     = len(pinned_names) + num_to_generate
    mandatory = "\n".join(f"- {name}" for name in pinned_names)

    prompt = f"""
You are a personal fitness coach building a complete workout plan.

User Profile:
- Goal: {user_stats['goal']}
- Fitness level: {user_stats['fitness_level']}
- Available equipment: {', '.join(user_stats['equipment'])}
- Has injuries: {user_stats['has_injuries']}
{disliked_str}
Last 7 days of activity:
{recent_str}

The user has requested these exercises be guaranteed in today's workout:
{mandatory}

Build a complete workout of EXACTLY {total} exercises total.
The mandatory exercises above MUST appear with their exact names.
Add {num_to_generate} complementary exercise(s) that balance the mandatory ones.

Rules:
- Only use the equipment listed above
- If the user has injuries, avoid exercises that stress injured areas while keeping recovery goals in mind
- Do not include any exercise the user has previously disliked
- Ensure the full workout is balanced across muscle groups

Respond ONLY with a JSON object containing ALL {total} exercises, no extra text:
{{
  "workout_summary": "brief description of the complete workout",
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


def build_replacement_prompt(user_stats: dict, last_7_days, rejected_exercises: list, kept_exercises: list, num_replacements: int) -> str:
    disliked = user_stats.get("disliked_exercises", [])
    if isinstance(disliked, str):
        disliked = ast.literal_eval(disliked)

    kept_names = [ex["name"] for ex in kept_exercises]

    prompt = f"""
You are a personal fitness coach. The user has rejected some exercises from their workout plan.

User Profile:
- Goal: {user_stats['goal']}
- Fitness level: {user_stats['fitness_level']}
- Available equipment: {', '.join(user_stats['equipment'])}
- Has injuries: {user_stats['has_injuries']}

Exercises already kept in the workout — do NOT duplicate these: {', '.join(kept_names) if kept_names else 'None'}
Exercises the user rejected and needs replacements for: {', '.join(rejected_exercises)}
Exercises the user has historically disliked — do NOT include: {', '.join(disliked) if disliked else 'None'}

Generate EXACTLY {num_replacements} replacement exercise(s).

Respond ONLY with a JSON object in this exact format, no extra text:
{{
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


# LLM calls

def _call_llm(prompt: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def generate_workout(user_stats: dict, last_7_days, rejected_exercises: list = None,
                     current_workout: dict = None, pinned_exercises: list = None) -> dict:

    # Replacement — only swap rejected slots, Python handles the merge
    if rejected_exercises and current_workout:
        kept             = [ex for ex in current_workout["exercises"] if ex["name"] not in rejected_exercises]
        num_replacements = len(rejected_exercises)
        prompt           = build_replacement_prompt(user_stats, last_7_days, rejected_exercises, kept, num_replacements)
        replacements     = _call_llm(prompt)
        current_workout["exercises"] = kept + replacements["exercises"]
        return current_workout

    # Fresh generation with pinned exercises from liked history
    if pinned_exercises:
        num_to_generate = max(2, 5 - len(pinned_exercises))
        prompt          = build_prompt_with_pinned(user_stats, last_7_days, pinned_exercises, num_to_generate)
        result          = _call_llm(prompt)

        # Safety net — verify all pinned exercises are present
        returned_names = [ex["name"] for ex in result["exercises"]]
        for name in pinned_exercises:
            if name not in returned_names:
                result["exercises"].insert(0, {
                    "name":         name,
                    "sets":         3,
                    "reps":         10,
                    "equipment":    "bodyweight",
                    "muscle_group": "varied",
                    "notes":        "User-selected exercise — adjust sets and reps to your level."
                })
        return result

    # Standard fresh generation
    prompt = build_prompt(user_stats, last_7_days)
    return _call_llm(prompt)


if __name__ == "__main__":
    from analysis import load_data, user_summary, last_7_days

    df_users, df_logs = load_data()
    stats  = user_summary("u_0001", df_users, df_logs)
    recent = last_7_days("u_0001", df_logs)

    print("Generating workout...")
    workout = generate_workout(stats, recent)
    print(json.dumps(workout, indent=2))