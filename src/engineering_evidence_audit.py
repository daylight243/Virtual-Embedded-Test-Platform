from pathlib import Path
import argparse
import sqlite3


def audit_database(database_path: Path) -> bool:

    if not database_path.is_file():
        print(
            f"Database not found: {database_path}"
        )
        return False

    connection = sqlite3.connect(
        database_path.resolve().as_uri() + "?mode=ro",
        uri=True,
    )

    try:
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        foreign_keys = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        runs = connection.execute(
            """
            SELECT
                test_id,
                COUNT(*) AS total,
                SUM(passed) AS passed
            FROM test_runs
            GROUP BY test_id
            ORDER BY test_id
            """
        ).fetchall()

        output_count = connection.execute(
            "SELECT COUNT(*) FROM fpga_outputs"
        ).fetchone()[0]

        fault_count = connection.execute(
            "SELECT COUNT(*) FROM fault_events"
        ).fetchone()[0]

        print("VETP Engineering Evidence Audit")
        print("=" * 45)

        print(
            f"Database: {database_path}"
        )

        print(
            f"Integrity: {integrity}"
        )

        print(
            f"Foreign-key violations: "
            f"{len(foreign_keys)}"
        )

        print(
            f"FPGA output rows: {output_count}"
        )

        print(
            f"Fault event rows: {fault_count}"
        )

        print("\nTest-run summary:")

        for test_id, total, passed in runs:
            failed = total - passed

            print(
                f"  {test_id}: "
                f"{total} total, "
                f"{passed} passed, "
                f"{failed} failed"
            )

        valid = (
            integrity == "ok"
            and len(foreign_keys) == 0
        )

        print()

        if valid:
            print("Database structural checks passed.")
        else:
            print("Database structural checks failed.")

        return valid

    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect VETP SQLite evidence "
            "without modifying the database."
        )
    )

    parser.add_argument(
        "database",
        type=Path,
        help="Path to the SQLite database",
    )

    args = parser.parse_args()

    return (
        0
        if audit_database(args.database)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())