# FitBuddy – AI Fitness Plan Generator using Gemini Models

Flow: Browser → FastAPI (app/main.py) → Jinja2 templates / Workout logic (routes.py) / Admin panel
→ Gemini AI Services → AI Plan Generator (updated_plan.py) → SQLite (fitbuddy.db)

## Run
```
python -m venv venv
venv\Scripts\activate        # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # Linux/Mac: cp .env.example .env  -> then add GEMINI_API_KEY
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000  (form)  and  http://127.0.0.1:8000/admin/users  (admin).

Get a free API key: https://aistudio.google.com/app/apikey

## Files
- app/main.py – FastAPI backend
- app/routes.py – workout logic, prompts, admin routes
- app/gemini_service.py – Gemini Pro (plan/update) + Gemini Flash (nutrition/recovery)
- app/updated_plan.py – parses/structures AI responses
- app/database.py, app/models.py – SQLite + SQLAlchemy (users, plans tables)
- app/templates/index.html, result.html, all_users.html
