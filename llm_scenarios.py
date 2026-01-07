import os
import json
from typing import List, Dict
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You generate BDD test scenarios in Gherkin.
- Use: Feature / Scenario / Given-When-Then
- Include at least one positive and one negative scenario.
- Domain: generic sample web app with login and dashboard.
Return ONLY valid Gherkin text, no explanations."""

HAPPY_KEYWORDS = ["login", "submit", "approve"]

def call_llm(requirements_text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": requirements_text},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def split_scenarios(gherkin_text: str) -> List[str]:
    blocks = []
    current = []
    for line in gherkin_text.splitlines():
        if line.strip().startswith("Scenario:"):
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks

def is_valid_scenario(text: str) -> bool:
    needed = ["Given", "When", "Then"]
    return all(k in text for k in needed)

def is_happy_path(text: str) -> bool:
    lower = text.lower()
    return all(k in lower for k in ["success", "valid"]) or "happy path" in lower

def contains_known_actions(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in HAPPY_KEYWORDS)

def validate_and_select_happy(gherkin_text: str) -> Dict[str, List[str]]:
    all_scenarios = split_scenarios(gherkin_text)
    valid = [s for s in all_scenarios if is_valid_scenario(s)]
    happy = [
        s for s in valid
        if contains_known_actions(s) and is_happy_path(s)
    ]
    return {"all": all_scenarios, "valid": valid, "happy": happy}

def write_feature_file(happy_scenarios: List[str], path: str) -> None:
    feature_header = (
        "Feature: LLM generated login flows\n"
        "  As a user of the sample web app\n"
        "  I want to login and access the dashboard\n"
        "  So that I can use the application features\n\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(feature_header)
        for s in happy_scenarios:
            lines = ["  " + line if line.strip() else "" for line in s.splitlines()]
            f.write("\n".join(lines))
            f.write("\n\n")

def generate_pipeline(requirements_text: str, feature_path: str = "features/login.feature") -> Dict:
    gherkin = call_llm(requirements_text)
    report = validate_and_select_happy(gherkin)

    validation_report = {
        "total": len(report["all"]),
        "valid": len(report["valid"]),
        "happy": len(report["happy"]),
        "has_required_actions": all(contains_known_actions(s) for s in report["happy"]),
    }

    if report["happy"]:
        write_feature_file(report["happy"], feature_path)

    return {
        "gherkin_raw": gherkin,
        "validation": validation_report,
        "selected_scenarios": report["happy"],
    }

if __name__ == "__main__":
    sample_reqs = """
    The system must allow a registered user to log in with a valid username and password
    and redirect to a dashboard on success. If credentials are invalid, an error message
    must be displayed and the user must remain on the login page.
    """
    result = generate_pipeline(sample_reqs)
    print(json.dumps(result["validation"], indent=2))
