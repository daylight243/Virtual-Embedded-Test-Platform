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

    connection.row_factory = sqlite3.Row

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

def save_device(
    connection: sqlite3.Connection,
    device_id: str,
    device_name: str,
    created_at_utc: str,
) -> None:

    connection.execute(
        """
        INSERT OR IGNORE INTO devices (
            device_id,
            device_name,
            created_at_utc
        )
        VALUES (?, ?, ?);
        """,
        (
            device_id,
            device_name,
            created_at_utc,
        ),
    )

def save_test_case(
    connection: sqlite3.Connection,
    test_id: str,
    test_name: str,
    description: str,
) -> None:

    connection.execute(
        """
        INSERT OR IGNORE INTO test_cases (
            test_id,
            test_name,
            description
        )
        VALUES (?, ?, ?);
        """,
        (
            test_id,
            test_name,
            description,
        ),
    )
def save_test_run(
    connection: sqlite3.Connection,
    run_id: str,
    device_id: str,
    test_id: str,
    started_at_utc: str,
    passed: bool,
    error_message: str | None = None,
) -> None:

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
            run_id,
            device_id,
            test_id,
            started_at_utc,
            int(passed),
            error_message,
        ),
    ) 

def save_fpga_output(
    connection: sqlite3.Connection,
    run_id: str,
    timestamp: int,
    state_code: int,
    fault_code: int,
    alarm: bool,
    shutdown: bool,
) -> None:

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
            run_id,
            timestamp,
            state_code,
            fault_code,
            int(alarm),
            int(shutdown),
        ),
    ) 

def save_fpga_outputs(
connection: sqlite3.Connection,
run_id: str,
outputs: list[tuple],
) -> None:

    rows = []

    for output in outputs:
        (
            timestamp,
            state_code,
            fault_code,
            alarm,
            shutdown,
        ) = output

        rows.append(
            (
                run_id,
                timestamp,
                state_code,
                fault_code,
                int(alarm),
                int(shutdown),
            )
        )

    connection.executemany(
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
        rows,
    )
    

def save_fault_event(
    connection: sqlite3.Connection,
    run_id: str,
    fault_type: str,
    start_timestamp: int,
    duration: int,
) -> None:

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
            run_id,
            fault_type,
            start_timestamp,
            duration,
        ),
    )

def save_fault_events(
    connection: sqlite3.Connection,
    run_id: str,
    fault_events: list[tuple],
) -> None:

    rows = []

    for fault_event in fault_events:
        (
            fault_type,
            start_timestamp,
            duration,
        ) = fault_event

        rows.append(
            (
                run_id,
                fault_type,
                start_timestamp,
                duration,
            )
        )

    connection.executemany(
        """
        INSERT INTO fault_events (
            run_id,
            fault_type,
            start_timestamp,
            duration
        )
        VALUES (?, ?, ?, ?);
        """,
        rows,
    )

def save_test_evidence(
    connection: sqlite3.Connection,
    device: tuple,
    test_case: tuple,
    test_run: tuple,
    fpga_outputs: list[tuple],
    fault_events: list[tuple],
) -> None:

    save_device(
        connection,
        *device,
    )

    save_test_case(
        connection,
        *test_case,
    )

    save_test_run(
        connection,
        *test_run,
    )

    save_fpga_outputs(
        connection,
        test_run[0],
        fpga_outputs,
    )

    save_fault_events(
        connection,
        test_run[0],
        fault_events,
    )

def count_rows(
    connection: sqlite3.Connection,
    table_name: str,
) -> int:

    allowed_tables = {
        "devices",
        "test_cases",
        "test_runs",
        "fpga_outputs",
        "fault_events",
    }

    if table_name not in allowed_tables:
        raise ValueError(
            f"Unsupported table: {table_name}"
        )

    cursor = connection.execute(
        f"SELECT COUNT(*) FROM {table_name};"
    )

    return cursor.fetchone()[0]

if __name__ == "__main__":

    device_data = (
        "PWR-001",
        "Power Controller",
        "2026-09-22T14:00:00+00:00",
    )

    test_case_data = (
        "TC-005",
        "Overcurrent Shutdown",
        (
            "Verify sustained overcurrent "
            "causes FAULT and shutdown."
        ),
    )

    test_run_data = (
        "RUN-DEMO-001",
        "PWR-001",
        "TC-005",
        "2026-09-22T14:05:00+00:00",
        True,
        None,
    )

    output_data = [
        (0, 0, 0, False, False),
        (1, 1, 0, False, False),
        (2, 2, 0, False, False),
        (3, 2, 3, False, False),
        (4, 2, 3, False, False),
        (5, 2, 3, False, False),
        (6, 3, 3, True, True),
    ]

    fault_data = [
        (
            "overcurrent",
            3,
            4,
        ),
    ]

    connection = connect_database()

    try:
        create_tables(connection)

        save_test_evidence(
            connection=connection,
            device=device_data,
            test_case=test_case_data,
            test_run=test_run_data,
            fpga_outputs=output_data,
            fault_events=fault_data,
        )

        connection.commit()

        print(
            "devices:",
            count_rows(
                connection,
                "devices",
            ),
        )

        print(
            "test_cases:",
            count_rows(
                connection,
                "test_cases",
            ),
        )

        print(
            "test_runs:",
            count_rows(
                connection,
                "test_runs",
            ),
        )

        print(
            "fpga_outputs:",
            count_rows(
                connection,
                "fpga_outputs",
            ),
        )

        print(
            "fault_events:",
            count_rows(
                connection,
                "fault_events",
            ),
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()