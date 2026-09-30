"""Gemini AI Services (API)
- Gemini Pro   -> Workout plan & updates
- Gemini Flash -> Nutrition / recovery tips
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PLAN_MODEL = os.getenv("PLAN_MODEL", "gemini-1.5-pro")
TIPS_MODEL = os.getenv("TIPS_MODEL", "gemini-1.5-flash")


def _generate(model_name: str, prompt: str) -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text


def generate_workout_plan(prompt: str) -> str:
    return _generate(PLAN_MODEL, prompt)


def update_workout_plan(prompt: str) -> str:
    return _generate(PLAN_MODEL, prompt)


def generate_tips(prompt: str) -> str:
    return _generate(TIPS_MODEL, prompt)
