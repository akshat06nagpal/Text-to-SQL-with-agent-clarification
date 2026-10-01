import sqlite3
from google.genai import errors

from clarify import clarify
from sql_generator import generate_sql, fix_sql
from validator import validate_sql
from executor import run_sql

MAX_FIX_ATTEMPTS = 1

def print_table(columns, rows, truncated):
    table = [columns] + [[str(v) for v in row] for row in rows]
    widths = [max(len(str(r[i])) for r in table) for i in range(len(columns))]
    for n, row in enumerate(table):
        print("  ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))
        if n == 0:
            print("  ".join("-" * w for w in widths))
    print(f"\n{len(rows)} row(s)" + (" (truncated, more rows exist)" if truncated else ""))

def answer(question):
    enriched, assumptions = clarify(question)
    if assumptions:
        print("\nAssumptions:")
        for a in assumptions:
            print(" -", a)

    sql = generate_sql(enriched)
    for attempt in range(MAX_FIX_ATTEMPTS + 1):
        print("\nSQL:\n" + sql + "\n")
        try:
            validate_sql(sql)
            columns, rows, truncated = run_sql(sql)
            print_table(columns, rows, truncated)
            return
        except (ValueError, sqlite3.Error) as e:
            print(f"Problem: {e}")
            if attempt == MAX_FIX_ATTEMPTS:
                print("Could not produce a working query for this question.")
                return
            print("Asking the model to fix it...")
            sql = fix_sql(enriched, sql, str(e))

if __name__ == "__main__":
    print("Text-to-SQL agent for Chinook. Type 'quit' to exit.")
    while True:
        q = input("\nQuestion: ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        try:
            answer(q)
        except errors.APIError as e:
            print(f"LLM error {e.code}: {e.message}")