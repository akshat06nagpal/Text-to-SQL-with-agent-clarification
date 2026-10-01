import json
import sqlite3
from llm import call_llm
from schema import get_schema_text

DB = "chinook.sqlite"
SCHEMA = get_schema_text(DB)

def data_date_range():
    conn = sqlite3.connect(DB)
    lo, hi = conn.execute(
        "SELECT MIN(InvoiceDate), MAX(InvoiceDate) FROM Invoice"
    ).fetchone()
    conn.close()
    return lo[:10], hi[:10]

LO, HI = data_date_range()

CLARIFY_PROMPT = f"""You review questions asked about a SQLite database,
BEFORE any SQL is written. Decide whether the question can be answered
unambiguously from the schema.

Ask for clarification ONLY when different reasonable interpretations would
give materially different results (e.g. "top" could be by revenue or by
number of purchases; a relative date has no clear reference point).
Do NOT ask about things you can work out from the schema.
If a sensible default exists, do not ask: state it as an assumption instead.
Ask at most 3 questions, each with 2-4 short options.

The database has invoice data from {LO} to {HI}.
You do not know today's real date.

Reply with JSON only, in exactly one of these shapes:
{{"status": "clear", "assumptions": ["..."]}}
{{"status": "needs_clarification", "questions": [{{"question": "...", "options": ["...", "..."]}}]}}

DATABASE SCHEMA:
{SCHEMA}
"""

def check_question(question):
    raw = call_llm(CLARIFY_PROMPT, question, json_mode=True)
    return json.loads(raw)

def clarify(question, max_rounds=2):
    """Returns (enriched_question, assumptions)."""
    for _ in range(max_rounds):
        result = check_question(question)
        if result["status"] == "clear":
            return question, result.get("assumptions", [])

        notes = []
        for q in result["questions"]:
            options = q.get("options", [])
            print("\n" + q["question"])
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            answer = input("> ").strip()
            # let the user type a number instead of the full option text
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                answer = options[int(answer) - 1]
            notes.append(f"Clarification - {q['question']} -> {answer}")
        question = question + "\n" + "\n".join(notes)
    return question, []

if __name__ == "__main__":
    for q in ["How many tracks are in the Rock genre?",
              "Who are the top customers?",
              "Show me sales from last quarter"]:
        print("\n" + "=" * 50)
        print("Q:", q)
        enriched, assumptions = clarify(q)
        print("\nFinal question:\n", enriched)
        print("Assumptions:", assumptions)