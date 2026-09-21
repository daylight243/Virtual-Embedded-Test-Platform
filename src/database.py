from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BUILD_DIR = PROJECT_ROOT / "build"

DATABASE_PATH = BUILD_DIR / "vetp.db"


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

    return connection


CREATE_TEST_RUNS_TABLE = '''
CREATE TABLE IF NOT EXISTS test_runs (
    run_id TEXT PRIMARY KEY,
    timestamp_utc TEXT NOT NULL,
    test_id TEXT NOT NULL,
    test_name TEXT NOT NULL,
    state_code INTEGER NOT NULL,
    fault_code INTEGER NOT NULL,
    alarm INTEGER NOT NULL,
    shutdown INTEGER NOT NULL,
    passed INTEGER NOT NULL
);
'''


def create_tables(
    connection: sqlite3.Connection,
) -> None:

    connection.execute(
        CREATE_TEST_RUNS_TABLE
    )

    connection.commit()


INSERT_TEST_RUN = '''
INSERT INTO test_runs (
    run_id,
    timestamp_utc,
    test_id,
    test_name,
    state_code,
    fault_code,
    alarm,
    shutdown,
    passed
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
'''


def insert_test_run(
    connection: sqlite3.Connection,
) -> None:

    connection.execute(
        INSERT_TEST_RUN,
        (
            "RUN-001",
            "2026-09-16T17:00:00+00:00",
            "TC-005",
            "Overcurrent Shutdown",
            3,
            3,
            1,
            1,
            1,
        ),
    )

    connection.commit()


def read_test_runs(
    connection: sqlite3.Connection,
) -> list[tuple]:

    cursor = connection.execute(
        '''
        SELECT
            run_id,
            test_id,
            test_name,
            state_code,
            fault_code,
            alarm,
            shutdown,
            passed
        FROM test_runs
        ORDER BY timestamp_utc;
        '''
    )

    return cursor.fetchall()


def initialize_database(
    database_path: Path = DATABASE_PATH,
) -> None:

    connection = connect_database(
        database_path
    )

    try:
        create_tables(
            connection
        )

    finally:
        connection.close()


if __name__ == "__main__":

    initialize_database()

   
    connection = connect_database()

    try:

        rows = read_test_runs(
            connection
        )

        print(
            f"Database ready: "
            f"{DATABASE_PATH}"
        )

        print(
            f"Stored test runs: "
            f"{len(rows)}"
        )

        for row in rows:
                    print(row)

    finally:
        connection.close()

