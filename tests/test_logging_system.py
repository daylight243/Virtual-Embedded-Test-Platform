import json

from test_logging import (
    TestRunLog,
    save_test_run_log,
)


def test_saved_log_is_valid_json(
    tmp_path,
):

    sample_test_log = TestRunLog(
        run_id="TC-TEST_001",
        test_id="TC-TEST",
        test_name="Logging Test",
        description=(
            "Test that a TestRunLog "
            "can be saved as valid JSON."
        ),
        started_at_utc=(
            "2026-01-01T00:00:00+00:00"
        ),

        measurements=(),

        hdl_inputs=(),
        expected_results=(),
        actual_results=(),

        verification_results=(),

        passed=True,

        errors=(),
    )

    path = save_test_run_log(
        test_log=sample_test_log,
        output_directory=tmp_path,
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["test_id"] == (
        sample_test_log.test_id
    )

    assert data["passed"] == (
        sample_test_log.passed
    )