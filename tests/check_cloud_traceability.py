import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT / "build" / "vetp.db"
)

run_id = input(
    "Enter the genuine VETP run_id: "
).strip()

connection = sqlite3.connect(
    DATABASE_PATH
)

try:
    cursor = connection.execute(
        """
        SELECT
            run_id,
            device_id,
            test_id,
            passed
        FROM test_runs
        WHERE run_id = ?;
        """,
        (run_id,),
    )

    row = cursor.fetchone()

    if row is None:
        print("Run not found in SQLite.")

    else:
        print("SQLite run found:")
        print(f"  run_id: {row[0]}")
        print(f"  device_id: {row[1]}")
        print(f"  test_id: {row[2]}")
        print(f"  passed: {bool(row[3])}")

finally:
    connection.close()