from validator import validate_sql
from executor import run_sql

should_pass = [
    "SELECT COUNT(*) FROM Track",
    "WITH t AS (SELECT * FROM Track) SELECT COUNT(*) FROM t",
    "SELECT Name FROM Artist UNION SELECT Name FROM Genre",
]
should_fail = [
    "DROP TABLE Track",
    "DELETE FROM Track",
    "UPDATE Track SET Name = 'x'",
    "SELECT 1; DELETE FROM Track",
    "PRAGMA table_info(Track)",
    "this is not sql",
    "",
]

for sql in should_pass:
    validate_sql(sql)
    print("OK     ", sql)

for sql in should_fail:
    try:
        validate_sql(sql)
        print("MISSED!", sql)          # this would be a bug
    except ValueError as e:
        print("BLOCKED", sql, "->", e)

# Execution layer: a real SELECT, then a write attempt through the read-only connection
print(run_sql("SELECT COUNT(*) FROM Track WHERE GenreId = 1"))
try:
    run_sql("DELETE FROM Track")
except Exception as e:
    print("Read-only protection worked:", e)