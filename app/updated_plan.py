"""AI Plan / Nutrition Generator
Parses the AI response and structures workout plan or nutrition tips."""
import re


def parse_plan(raw_text: str) -> str:
    """Clean the model output: strip code fences and extra blank lines."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:markdown|md)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_tips(raw_text: str) -> dict:
    """Split the tips response into Nutrition and Recovery sections."""
    text = parse_plan(raw_text)
    sections = {"nutrition": "", "recovery": ""}
    parts = re.split(r"(?im)^#+\s*(nutrition|recovery)[^\n]*\n", text)
    # parts = [before, 'Nutrition', body, 'Recovery', body]
    if len(parts) >= 3:
        for i in range(1, len(parts) - 1, 2):
            sections[parts[i].lower()] = parts[i + 1].strip()
    else:
        sections["nutrition"] = text
    return sections


def structure_result(plan_text: str, tips_text: str) -> dict:
    return {"plan": parse_plan(plan_text), "tips": parse_tips(tips_text)}
