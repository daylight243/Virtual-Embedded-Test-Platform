from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BUILD_DIR = PROJECT_ROOT / "build"

DATABASE_PATH = BUILD_DIR / "vetp.db"

SQL_DIR = PROJECT_ROOT / "sql"

SCHEMA_PATH = (
    SQL_DIR
    / "schema.sql"
)


def connect_database(
    database_path: Path = DATABASE_PATH,
) -> sqlite3.Connection:

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        database_path
    )

    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return connection


def create_tables(
    connection: sqlite3.Connection,
) -> None:

    schema_sql = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(
        schema_sql
    )

    connection.commit()


def list_tables(
    connection: sqlite3.Connection,
) -> list[str]:

    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
    )

    return [
        row[0]
        for row
        in cursor.fetchall()
    ]


if __name__ == "__main__":

    connection = connect_database()

    try:

        create_tables(
            connection
        )

        connection.execute(
            """
            INSERT INTO devices (
                device_id,
                device_name,
                created_at_utc
            )
            VALUES (?, ?, ?);
            """,
            (
                "PWR-001",
                "Power Controller",
                "2026-09-16T20:00:00+00:00",
            ),
        )

       
        connection.execute(
            """
            INSERT INTO test_cases (
                test_id,
                test_name,
                description
            )
            VALUES (?, ?, ?);
            """,
            (
                "TC-005",
                "Overcurrent Shutdown",
                (
                    "Verify sustained overcurrent "
                    "causes FAULT and shutdown."
                ),
            ),
        )

       

        connection.execute(
            """
            INSERT INTO test_runs (
                run_id,
                device_id,
                test_id,
                started_at_utc,
                passed,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                "RUN-DEMO-001",
                "PWR-001",
                "TC-005",
                "2026-09-16T20:05:00+00:00",
                1,
                None,
            ),
        )

        

        connection.execute(
            """
            INSERT INTO fpga_outputs (
                run_id,
                timestamp,
                state_code,
                fault_code,
                alarm,
                shutdown
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                "RUN-DEMO-001",
                6,
                3,
                3,
                1,
                1,
            ),
        )

        
        connection.execute(
            """
            INSERT INTO fault_events (
                run_id,
                fault_type,
                start_timestamp,
                duration
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                "RUN-DEMO-001",
                "overcurrent",
                3,
                4,
            ),
        )


        connection.commit()

       
        for table_name in list_tables(
            connection
        ):
            print(table_name)

    finally:

        connection.close()