# AI Fitness Tracker

A Python-based fitness analytics application that generates personalised workout plans and tracks progress over time. Built as a foundation for a future AI-powered fitness platform.

This project was developed as part of the Developers Institute GenAI & Machine Learning Bootcamp (Hackathon Topic 2).

---

## Project Overview

The app simulates 500 user profiles with realistic fitness data and provides:
- A global dashboard showing aggregate stats across all users
- Individual user dashboards with personal progress charts and a live muscle group diagram
- AI-generated daily workout suggestions via a Groq LLM, personalised by equipment, injuries, and past feedback
- A feedback loop where users like or reject individual exercises — preferences are persisted and used in future recommendations
- Statistical analysis of fitness patterns using SciPy

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.12 |
| Data | Pandas, NumPy, Faker |
| Visualisation | Matplotlib, Seaborn |
| Statistics | SciPy |
| Dashboard | Streamlit |
| LLM | Groq API (LLaMA 3.3 70B) |
| Version Control | Git / GitHub |

---

## Project Structure

```
AI-Fitness-App-Hackathon/
├── data/
│   ├── raw/
│   │   ├── users.json              ← 500 generated user profiles
│   │   └── saved_workouts.json     ← user saved workouts (generated at runtime)
│   └── processed/
│       ├── users.csv               ← flat user profiles
│       └── logs.csv                ← flat daily activity logs
├── notebooks/
│   └── statistical_analysis.ipynb ← SciPy analysis with results and commentary
├── src/
│   ├── generate_users.py           ← simulates 500 user profiles and daily logs
│   ├── load_data.py                ← flattens JSON into two DataFrames
│   ├── analysis.py                 ← aggregations, summaries, functional tools
│   ├── models.py                   ← User class (OOP)
│   ├── stats_analysis.py           ← ANOVA, linear regression, paired t-test
│   ├── visualizations.py           ← all Matplotlib/Seaborn chart functions
│   ├── muscle_map.py               ← front/back body diagram with muscle highlights
│   ├── workout_generator.py        ← Groq LLM integration and saved workouts
│   └── app.py                      ← Streamlit dashboard
├── .env                            ← API key (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/TamirPalay/AI-Fitness-App-Hackathon.git
cd AI-Fitness-App-Hackathon
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```
Get a free API key at [console.groq.com](https://console.groq.com).

### 4. Generate the data
```bash
python src/generate_users.py
python src/load_data.py
```

### 5. Run the dashboard
```bash
streamlit run src/app.py
```

---

## Features

### Global Dashboard
- Aggregate metrics across all 500 users: avg daily steps, calories, workout duration, and most popular workout type
- Bar charts showing average calorie burn and session frequency by workout type

### User Dashboard
- Select any user by number (1–500) with a personalised sidebar summary
- Profile overview: goal, fitness level, equipment, preferred workouts, and injury details
- Personal activity metrics and progress charts (steps over time, calories over time, workout frequency)
- Injury warnings displayed with body part, severity, and coaching notes

### AI Workout Generation
- Sends the user's profile and last 7 days of activity to Groq (LLaMA 3.3 70B)
- Returns a structured JSON workout plan with 4–6 exercises including sets, reps, equipment, and coaching notes
- Each exercise is rendered as a colour-coded card (colour reflects muscle group)
- **Like (❤️)** or **Reject (👎)** individual exercises — rejected exercises are swapped out via a targeted LLM call that only replaces the rejected slots, keeping accepted exercises intact
- Liked and disliked exercises are persisted to the user profile on save and fed back into future LLM prompts
- Saved workouts can be revisited from the dashboard

### Muscle Group Diagram
- Front and back body silhouette rendered alongside each workout
- Active muscle groups highlighted in their card colour
- Primary muscle groups shown in full colour, secondary groups in a lighter shade
- Inactive muscle groups displayed in neutral grey

### Statistical Analysis (see notebook)
- **ANOVA:** Confirms significant difference in calorie burn across workout types (F=847.82, p≈0.0)
- **Linear Regression:** Models a user's step trend and predicts the next 7 days of activity
- **Paired T-Test:** Tests whether workout intensity affects user satisfaction ratings

---

## User Profile Schema

Each user profile contains:

```json
{
  "user_id": "u_0001",
  "name": "Timothy Saunders",
  "age": 19,
  "weight_kg": 84.3,
  "height_cm": 181,
  "goal": "strength",
  "fitness_level": "advanced",
  "equipment": ["bodyweight", "dumbbells", "barbells"],
  "injuries": [
    {
      "body_part": "lower_back",
      "severity": "sensitive",
      "notes": "Recovered but monitor for discomfort."
    }
  ],
  "preferred_workouts": ["HIIT", "Strength"],
  "liked_exercises": [],
  "disliked_exercises": [],
  "daily_logs": [
    {
      "date": "2026-05-30",
      "steps": 9500,
      "calories_burned": 480,
      "workout_type": "HIIT",
      "duration_minutes": 45,
      "workout_rating": 4
    }
  ]
}
```

---

## Known Limitations

- **Simulated data only.** All user profiles and activity logs are generated. Real-world data would produce more meaningful statistical results.
- **Ratings are randomly generated.** The paired t-test result is limited by this — a real preference signal will emerge as actual user feedback accumulates through the like/reject system.
- **No authentication.** Users are selected by number, not by login. This is intentional for a prototype with simulated data.
- **Calorie values are not tied to body weight or age.** A production model would factor in BMR and user biometrics for more accurate estimates.

---

## Future Development

This project is the foundation for a full AI fitness platform. Planned next steps:

- **ML exercise substitution model** — replace the LLM with a trained model that learns exercise equivalences based on equipment, injuries, and accumulated like/dislike feedback
- **Real user data** — replace the simulator with actual input forms and a database backend
- **Exercise library** — a structured database of exercises tagged by muscle group, equipment, and injury contraindications
- **Progress tracking** — detect plateaus, celebrate milestones, and adapt workout difficulty over time
- **BMI and fitness scoring** — derive additional user metrics from height, weight, and activity data for richer personalisation

---

## Author

**Tamir Palay**
Data Analytics & AI/ML — Developers Institute Bootcamp
[typalay@gmail.com](mailto:typalay@gmail.com)