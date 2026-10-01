import sqlite3
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from database import (
    connect_database,
    create_tables,
)

from database_integration import save_completed_run


@dataclass(frozen=True)
class FakeInjection:
    fault: str
    start_timestamp: int
    duration: int

    def validate(self):
        assert self.duration > 0


def sample(
    run_id="TEST-001",
    passed=True,
):
    case = SimpleNamespace(
        test_id="TC-005",
        name="Overcurrent Shutdown",
        description="Integration test",
        fault_injections=(
            FakeInjection(
                "overcurrent",
                3,
                4,
            ),
        ),
    )

    log = SimpleNamespace(
        run_id=run_id,
        test_id="TC-005",
        started_at_utc="2026-09-30T00:00:00+00:00",
        passed=passed,
        errors=(),
        actual_results=(
            {
                "timestamp": 3,
                "state_code": 2,
                "fault_code": 3,
                "alarm": 0,
                "shutdown": 0,
            },
            {
                "timestamp": 6,
                "state_code": 3,
                "fault_code": 3,
                "alarm": 1,
                "shutdown": 1,
            },
        ),
    )

    return case, log


@pytest.fixture
def connection(tmp_path):

    conn = connect_database(
        tmp_path / "test.db"
    )

    create_tables(conn)

    yield conn

    conn.close()


def test_save_outputs_faults_and_failure(
    connection,
):

    case, log = sample(
        passed=False
    )

    save_completed_run(
        connection,
        case,
        log,
    )

    connection.commit()

    assert connection.execute(
        "SELECT passed FROM test_runs"
    ).fetchone()[0] == 0

    outputs = connection.execute(
        """
        SELECT
            timestamp,
            state_code,
            fault_code,
            alarm,
            shutdown
        FROM fpga_outputs
        ORDER BY timestamp
        """
    ).fetchall()

    assert [
        tuple(row)
        for row in outputs
    ] == [
        (3, 2, 3, 0, 0),
        (6, 3, 3, 1, 1),
    ]

    assert tuple(
        connection.execute(
            """
            SELECT
                fault_type,
                start_timestamp,
                duration
            FROM fault_events
            """
        ).fetchone()
    ) == (
        "overcurrent",
        3,
        4,
    )


def test_duplicate_run_rolls_back(
    connection,
):

    case, log = sample()

    save_completed_run(
        connection,
        case,
        log,
    )

    connection.commit()

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        save_completed_run(
            connection,
            case,
            log,
        )

    connection.rollback()

    assert connection.execute(
        "SELECT COUNT(*) FROM test_runs"
    ).fetchone()[0] == 1

    assert connection.execute(
        "SELECT COUNT(*) FROM fpga_outputs"
    ).fetchone()[0] == 2


def test_bad_child_rolls_back_all_new_rows(
    connection,
):

    case, log = sample(
        "ROLLBACK-001"
    )

    # Force an invalid FPGA output.
    # The Chapter 2 schema requires a timestamp.

    log.actual_results[1][
        "timestamp"
    ] = None

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        save_completed_run(
            connection,
            case,
            log,
        )

    connection.rollback()

    assert connection.execute(
        "SELECT COUNT(*) FROM test_runs"
    ).fetchone()[0] == 0