import sqlite3

from dashboard_logic import (
    state_name,
    fault_name,
    find_state_transitions,
    find_fault_transitions,
)

from database_queries import (
    count_test_runs,
    count_runs_by_result,
    calculate_pass_rate,
)


def test_state_translation():
    assert state_name(0) == "IDLE"
    assert state_name(3) == "FAULT"


def test_fault_translation():
    assert fault_name(0) == "NONE"
    assert fault_name(3) == "OC"


def test_unknown_state():
    assert (
        state_name(99)
        == "UNKNOWN (99)"
    )


def test_state_transitions():
    outputs = [
        {
            "timestamp": 0,
            "state_code": 0,
        },
        {
            "timestamp": 1,
            "state_code": 0,
        },
        {
            "timestamp": 2,
            "state_code": 1,
        },
        {
            "timestamp": 3,
            "state_code": 2,
        },
        {
            "timestamp": 4,
            "state_code": 2,
        },
        {
            "timestamp": 5,
            "state_code": 3,
        },
        {
            "timestamp": 6,
            "state_code": 3,
        },
    ]

    transitions = find_state_transitions(
        outputs
    )

    assert transitions == [
        {
            "Timestamp": 0,
            "State": "IDLE",
            "State Code": 0,
        },
        {
            "Timestamp": 2,
            "State": "STARTUP",
            "State Code": 1,
        },
        {
            "Timestamp": 3,
            "State": "RUNNING",
            "State Code": 2,
        },
        {
            "Timestamp": 5,
            "State": "FAULT",
            "State Code": 3,
        },
    ]


def test_fault_transitions():
    outputs = [
        {
            "timestamp": 0,
            "fault_code": 0,
        },
        {
            "timestamp": 1,
            "fault_code": 0,
        },
        {
            "timestamp": 2,
            "fault_code": 3,
        },
        {
            "timestamp": 3,
            "fault_code": 3,
        },
        {
            "timestamp": 4,
            "fault_code": 3,
        },
    ]

    transitions = find_fault_transitions(
        outputs
    )

    assert transitions == [
        {
            "Timestamp": 0,
            "Fault": "NONE",
            "Fault Code": 0,
        },
        {
            "Timestamp": 2,
            "Fault": "OC",
            "Fault Code": 3,
        },
    ]


def test_database_counts():
    connection = sqlite3.connect(
        ":memory:"
    )

    try:
        connection.execute(
            """
            CREATE TABLE test_runs (
                run_id TEXT PRIMARY KEY,
                passed INTEGER NOT NULL
            );
            """
        )

        connection.executemany(
            """
            INSERT INTO test_runs (
                run_id,
                passed
            )
            VALUES (?, ?);
            """,
            [
                ("RUN-001", 1),
                ("RUN-002", 1),
                ("RUN-003", 1),
                ("RUN-004", 0),
            ],
        )

        connection.commit()

        total = count_test_runs(
            connection
        )

        passed = count_runs_by_result(
            connection,
            True,
        )

        failed = count_runs_by_result(
            connection,
            False,
        )

        pass_rate = calculate_pass_rate(
            connection
        )

        assert total == 4
        assert passed == 3
        assert failed == 1
        assert pass_rate == 75.0

    finally:
        connection.close()