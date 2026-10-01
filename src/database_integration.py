import sqlite3
from datetime import datetime, timezone

from database import save_test_evidence
from fpga_test_cases import EngineeringTestCase
from test_logging import TestRunLog


DEVICE_ID = "PWR-001"
DEVICE_NAME = "Power Controller"


def save_completed_run(
    connection: sqlite3.Connection,
    test_case: EngineeringTestCase,
    test_log: TestRunLog,
) -> None:
    """Stage one complete run; caller owns commit/rollback."""

    if test_log.test_id != test_case.test_id:
        raise ValueError(
            "Test case and test log IDs do not match."
        )

    if not test_log.run_id:
        raise ValueError(
            "A completed run must have a run ID."
        )

    outputs = []

    for result in test_log.actual_results:
        outputs.append(
            (
                result["timestamp"],
                result["state_code"],
                result["fault_code"],
                result["alarm"],
                result["shutdown"],
            )
        )


    injections = getattr(
        test_case,
        "fault_injections",
        (),
    )

    fault_events = []

    for injection in injections:
        injection.validate()

        fault_events.append(
            (
                injection.fault,
                injection.start_timestamp,
                injection.duration,
            )
        )

    save_test_evidence(
        connection=connection,
        device=(
            DEVICE_ID,
            DEVICE_NAME,
            datetime.now(timezone.utc).isoformat(),
        ),
        test_case=(
            test_case.test_id,
            test_case.name,
            test_case.description,
        ),
        test_run=(
            test_log.run_id,
            DEVICE_ID,
            test_log.test_id,
            test_log.started_at_utc,
            test_log.passed,
            (
                "; ".join(test_log.errors)
                if test_log.errors
                else None
            ),
        ),
        fpga_outputs=outputs,
        fault_events=fault_events,
    )