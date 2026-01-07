import json
from llm_scenarios import generate_pipeline
import subprocess

REQS = """
The system must provide a login form with email and password fields.
Successful login with valid credentials redirects the user to the dashboard and shows a welcome message.
Unsuccessful login with invalid credentials shows an error and does not redirect.
"""

if __name__ == "__main__":
    result = generate_pipeline(REQS)
    print("=== Validation report ===")
    print(json.dumps(result["validation"], indent=2))
    print("=== Selected happy-path scenarios ===")
    for s in result["selected_scenarios"]:
        print(s)
        print("-" * 60)

    approve = input("Approve running automated tests? (yes/no): ").strip().lower()
    with open("manual_approval.txt", "w", encoding="utf-8") as f:
        f.write(f"approved={approve}\n")

    if approve == "yes":
        print("Running behave...")
        subprocess.run(["behave", "features/login.feature"], check=False)
    else:
        print("Execution cancelled by user.")
