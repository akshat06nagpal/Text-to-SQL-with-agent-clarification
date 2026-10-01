from llm import call_llm
from schema import get_schema_text

SCHEMA = get_schema_text("chinook.sqlite")

SQL_PROMPT = f"""You are an expert SQLite analyst.
Given a user's question, write one SQLite SELECT query that answers it,
using only the tables and columns in the schema below.
If the question includes lines starting with "Clarification", treat them
as the user's answers and follow them.
Return only the SQL, with no explanation and no markdown fences.

DATABASE SCHEMA:
{SCHEMA}
"""

def _clean(sql):
    return sql.replace("```sql", "").replace("```", "").strip()

def generate_sql(question):
    return _clean(call_llm(SQL_PROMPT, question))

def fix_sql(question, bad_sql, error):
    user_text = (
        f"{question}\n\n"
        f"Your previous attempt:\n{bad_sql}\n\n"
        f"It failed with this error:\n{error}\n\n"
        "Return a corrected SQLite SELECT query."
    )
    return _clean(call_llm(SQL_PROMPT, user_text))

if __name__ == "__main__":
    print(generate_sql(input("Ask a question: ")))