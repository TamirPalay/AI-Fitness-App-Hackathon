# AI Fitness Tracker

A Python-based fitness analytics application that generates personalised workout plans and tracks progress over time. Built as a foundation for a future AI-powered fitness platform.

This project was developed as part of the Developers Institute GenAI & Machine Learning Bootcamp (Hackathon Topic 2).

---

## Project Overview

The app simulates 500 user profiles with realistic fitness data and provides:
- A global dashboard showing aggregate stats across all users
- Individual user dashboards with personal progress charts
- AI-generated daily workout suggestions via a Groq LLM
- A feedback loop where users accept or reject exercises and regenerate replacements
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
- Average daily steps, calories burned, and workout duration across all 500 users
- Bar charts showing calorie burn and workout frequency by workout type

### User Dashboard
- Select any user by number (1–500)
- Profile summary including goal, fitness level, equipment, and injuries
- Personal activity metrics and progress charts
- Steps and calories over time (line plots)
- Personal workout frequency (bar chart)

### AI Workout Generation
- Sends a user's profile and last 7 days of activity to the Groq LLM
- Returns a structured JSON workout plan (4–6 exercises with sets, reps, equipment, and coaching notes)
- User can thumbs down individual exercises and regenerate replacements
- Accepted workouts can be saved and revisited

### Statistical Analysis (see notebook)
- **ANOVA:** Confirms significant difference in calorie burn across workout types (F=847.82, p≈0.0)
- **Linear Regression:** Models step trends and predicts the next 7 days of activity
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
- **`disliked_exercises` is not yet persisted.** The field exists in the schema and the UI captures rejections, but rejected exercises are not yet written back to the user profile after each session.
- **Ratings are randomly generated.** The paired t-test result is limited by this — a real preference signal would emerge from actual user feedback over time.
- **No authentication.** Users are selected by number, not by login. This is intentional for a prototype with fake data.

---

## Future Development

This project is the foundation for a full AI fitness platform. Planned next steps:

- **ML exercise substitution model** — replace the LLM with a trained model that learns exercise equivalences based on equipment, injuries, and user feedback
- **Persist user feedback** — write accepted/rejected exercises back to user profiles to build a real training dataset
- **Real user data** — replace the simulator with actual input forms and a database backend
- **Exercise library** — a structured database of exercises tagged by muscle group, equipment, and injury contraindications
- **Progress tracking** — detect plateaus, celebrate milestones, and adapt workout difficulty over time

---

## Author

**Tamir Palay**
Data Analytics & AI/ML — Developers Institute Bootcamp
[typalay@gmail.com](mailto:typalay@gmail.com)