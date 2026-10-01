import sqlite3

def get_schema_text(db_path, sample_rows=3):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # sqlite_master stores the original CREATE TABLE statement in the "sql" column
    cursor.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tables = cursor.fetchall()

    parts = []
    for table_name, create_sql in tables:
        parts.append(create_sql + ";")

        # Grab a few example rows so the LLM sees real values
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {sample_rows};')
        rows = cursor.fetchall()
        col_names = [d[0] for d in cursor.description]

        parts.append(f"-- Sample rows from {table_name} ({', '.join(col_names)}):")
        for row in rows:
            parts.append(f"-- {row}")
        parts.append("")  # blank line between tables

    conn.close()
    return "\n".join(parts)


if __name__ == "__main__":
    print(get_schema_text("chinook.sqlite"))