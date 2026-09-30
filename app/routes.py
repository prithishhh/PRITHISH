"""Workout Logic (routes.py + AI)
Processes user input, builds prompts and manages the AI workflow.
Also contains the Admin Panel (view-all-users) routes."""
import markdown
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, WorkoutPlan
from . import gemini_service as ai
from .updated_plan import structure_result, parse_plan

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.filters["md"] = lambda t: markdown.markdown(t or "", extensions=["tables"])


# ---------- Prompt builders ----------
def build_plan_prompt(user: User) -> str:
    return (
        f"You are a certified fitness coach. Create a 7-day workout plan.\n"
        f"Name: {user.name}\nAge: {user.age}\nWeight: {user.weight} kg\n"
        f"Goal: {user.goal}\nIntensity: {user.intensity}\n\n"
        "Format in Markdown: one heading per day, exercises with sets x reps, "
        "include a rest day and a short warm-up/cool-down. Keep it practical."
    )


def build_tips_prompt(user: User) -> str:
    return (
        f"Give nutrition and recovery tips for a {user.age}-year-old, {user.weight} kg person "
        f"whose goal is '{user.goal}' with {user.intensity} intensity training.\n"
        "Reply in Markdown with exactly two sections: '## Nutrition' and '## Recovery'. "
        "Use short bullet points."
    )


def build_update_prompt(plan: WorkoutPlan, feedback: str) -> str:
    return (
        "Here is the user's current workout plan:\n\n"
        f"{plan.updated_plan or plan.original_plan}\n\n"
        f"The user's feedback / change request: {feedback}\n\n"
        "Return the full updated 7-day plan in Markdown."
    )


# ---------- User pages ----------
@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"error": None})


@router.post("/generate")
def generate(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    user = User(name=name, age=age, weight=weight, goal=goal, intensity=intensity)
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        plan_raw = ai.generate_workout_plan(build_plan_prompt(user))   # Gemini Pro
        tips_raw = ai.generate_tips(build_tips_prompt(user))            # Gemini Flash
    except Exception as e:
        db.delete(user)
        db.commit()
        return templates.TemplateResponse(
            request, "index.html", {"error": f"AI error: {e}"}, status_code=502
        )

    result = structure_result(plan_raw, tips_raw)
    plan = WorkoutPlan(
        user_id=user.id, goal=goal, intensity=intensity, original_plan=result["plan"]
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return templates.TemplateResponse(
        request, "result.html", {"user": user, "plan": plan, "tips": result["tips"]}
    )


@router.post("/plan/{plan_id}/update")
def update_plan(
    request: Request,
    plan_id: int,
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    plan = db.get(WorkoutPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    plan.updated_plan = parse_plan(ai.update_workout_plan(build_update_prompt(plan, feedback)))
    db.commit()
    db.refresh(plan)

    tips = structure_result("", ai.generate_tips(build_tips_prompt(plan.user)))["tips"]
    return templates.TemplateResponse(
        request, "result.html", {"user": plan.user, "plan": plan, "tips": tips}
    )


# ---------- Admin Panel ----------
@router.get("/admin/users")
def all_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(request, "all_users.html", {"users": users})


@router.get("/admin/plan/{plan_id}")
def admin_view_plan(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(WorkoutPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    return templates.TemplateResponse(
        request, "result.html", {"user": plan.user, "plan": plan, "tips": None}
    )


@router.post("/admin/users/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)
