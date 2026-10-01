import sqlglot
from sqlglot import exp

# Statement types that must never appear anywhere in the query.
# Built with getattr/hasattr because class names differ slightly between sqlglot versions.
_FORBIDDEN_NAMES = ["Insert", "Update", "Delete", "Drop", "Create", "Alter",
                    "AlterTable", "Command", "Pragma", "Merge", "Attach"]
FORBIDDEN = tuple(getattr(exp, n) for n in _FORBIDDEN_NAMES if hasattr(exp, n))

def validate_sql(sql):
    """Raises ValueError unless sql is exactly one read-only SELECT."""
    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except sqlglot.errors.ParseError as e:
        raise ValueError(f"SQL could not be parsed: {e}")

    if len(statements) != 1:
        raise ValueError("Exactly one SQL statement is allowed.")

    stmt = statements[0]
    if not isinstance(stmt, (exp.Select, exp.Union)):
        raise ValueError("Only SELECT queries are allowed.")

    if stmt.find(*FORBIDDEN):
        raise ValueError("Query contains a forbidden operation.")

    return sql