import sqlite3
import time

DB = "chinook.sqlite"

def run_sql(sql, max_rows=100, timeout_s=5):
    # mode=ro opens the file read-only, so even if the validator missed
    # something, SQLite itself refuses to write.
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    start = time.time()
    def abort_if_slow():
        # SQLite calls this every 10,000 steps; returning 1 aborts the query
        return 1 if time.time() - start > timeout_s else 0
    conn.set_progress_handler(abort_if_slow, 10000)

    try:
        cursor = conn.execute(sql)
        columns = [d[0] for d in cursor.description]
        rows = cursor.fetchmany(max_rows + 1)   # fetch one extra to detect truncation
        truncated = len(rows) > max_rows
        return columns, rows[:max_rows], truncated
    finally:
        conn.close()