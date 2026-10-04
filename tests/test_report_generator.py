from pathlib import Path

import pytest

import report_generator

from report_generator import (
    build_test_report,
    build_fpga_timeline,
    build_fault_event_table,
    save_test_report,
    calculate_campaign_pass_rate,
    build_campaign_report,
)

from test_logging import (
    TestRunLog,
    CampaignSummary,
)


# --------------------------------------------------
# Shared test fixture
# --------------------------------------------------

@pytest.fixture
def sample_test_log():
    """
    Create a small controlled TestRunLog for testing
    the report generator.

    This is test evidence only. It does not modify
    the real VETP campaign database.
    """

    return TestRunLog(
        run_id="TC-TEST_20261003T120000000000Z",
        test_id="TC-TEST",
        test_name="Report Generator Test",
        description=(
            "Verify that the report generator "
            "correctly represents stored test evidence."
        ),
        started_at_utc="2026-10-03T12:00:00+00:00",

        measurements=(
            {
                "timestamp": 0,
                "voltage": 12.0,
                "current": 1.0,
                "temperature": 25.0,
            },
        ),

        hdl_inputs=(
            {
                "timestamp": 0,
                "start": 1,
                "uv": 0,
                "ov": 0,
                "oc": 0,
                "ot": 0,
            },
        ),

        expected_results=(
            {
                "timestamp": 0,
                "expected_state": "RUNNING",
            },
        ),

        actual_results=(
            {
                "timestamp": 0,
                "state_code": "010",
                "state_name": "RUNNING",
                "fault_code": "000",
                "fault_name": "NONE",
                "alarm": 0,
                "shutdown": 0,
            },
            {
                "timestamp": 1,
                "state_code": "011",
                "state_name": "FAULT",
                "fault_code": "011",
                "fault_name": "OC",
                "alarm": 1,
                "shutdown": 1,
            },
        ),

        verification_results=(
            {
                "timestamp": 0,
                "passed": True,
                "message": "Expected state observed.",
            },
        ),

        passed=True,

        errors=(),
    )


# --------------------------------------------------
# Test 1
# Report contains the genuine run ID
# --------------------------------------------------

def test_report_contains_run_id(
    sample_test_log,
):
    report = build_test_report(
        sample_test_log,
        fault_events=(),
    )

    assert sample_test_log.run_id in report


# --------------------------------------------------
# Test 2
# Report contains PASS and FAIL correctly
# --------------------------------------------------

def test_report_contains_pass_and_fail():
    passed_log = TestRunLog(
        run_id="RUN-PASS",
        test_id="TC-PASS",
        test_name="Passing Test",
        description="Controlled passing test.",
        started_at_utc="2026-10-03T12:00:00+00:00",
        measurements=(),
        hdl_inputs=(),
        expected_results=(),
        actual_results=(),
        verification_results=(),
        passed=True,
        errors=(),
    )

    failed_log = TestRunLog(
        run_id="RUN-FAIL",
        test_id="TC-FAIL",
        test_name="Failing Test",
        description="Controlled failing test.",
        started_at_utc="2026-10-03T12:01:00+00:00",
        measurements=(),
        hdl_inputs=(),
        expected_results=(),
        actual_results=(),
        verification_results=(),
        passed=False,
        errors=(
            "Expected state did not match actual state.",
        ),
    )

    passed_report = build_test_report(
        passed_log,
        fault_events=(),
    )

    failed_report = build_test_report(
        failed_log,
        fault_events=(),
    )

    assert "**Result: PASS**" in passed_report
    assert "**Result: FAIL**" in failed_report

    assert (
        "Expected state did not match actual state."
        in failed_report
    )


# --------------------------------------------------
# Test 3
# FPGA timeline preserves output ordering
# --------------------------------------------------

def test_fpga_timeline_preserves_order():
    actual_results = (
        {
            "timestamp": 0,
            "state_code": "000",
            "fault_code": "000",
            "alarm": 0,
            "shutdown": 0,
        },
        {
            "timestamp": 1,
            "state_code": "001",
            "fault_code": "000",
            "alarm": 0,
            "shutdown": 0,
        },
        {
            "timestamp": 2,
            "state_code": "010",
            "fault_code": "000",
            "alarm": 0,
            "shutdown": 0,
        },
        {
            "timestamp": 3,
            "state_code": "011",
            "fault_code": "011",
            "alarm": 1,
            "shutdown": 1,
        },
    )

    timeline = build_fpga_timeline(
        actual_results
    )

    position_0 = timeline.index(
        "| 0 | 000 | 000 | 0 | 0 |"
    )

    position_1 = timeline.index(
        "| 1 | 001 | 000 | 0 | 0 |"
    )

    position_2 = timeline.index(
        "| 2 | 010 | 000 | 0 | 0 |"
    )

    position_3 = timeline.index(
        "| 3 | 011 | 011 | 1 | 1 |"
    )

    assert (
        position_0
        < position_1
        < position_2
        < position_3
    )


# --------------------------------------------------
# Test 4
# Empty fault-event list is handled correctly
# --------------------------------------------------

def test_empty_fault_events():
    fault_table = build_fault_event_table(
        ()
    )

    assert (
        fault_table
        == "No fault injections were recorded."
    )


# --------------------------------------------------
# Test 5
# Report file is saved successfully
# --------------------------------------------------

def test_save_test_report(
    sample_test_log,
    tmp_path,
    monkeypatch,
):
    """
    Save into pytest's temporary directory instead
    of the real build/reports directory.
    """

    temporary_reports_directory = (
        tmp_path / "reports"
    )

    monkeypatch.setattr(
        report_generator,
        "REPORTS_DIR",
        temporary_reports_directory,
    )

    report_text = build_test_report(
        sample_test_log,
        fault_events=(),
    )

    report_path = save_test_report(
        sample_test_log,
        report_text,
    )

    assert report_path.exists()
    assert report_path.is_file()

    saved_text = report_path.read_text(
        encoding="utf-8"
    )

    assert saved_text == report_text
    assert sample_test_log.run_id in saved_text

    assert (
        report_path.parent
        == temporary_reports_directory
    )


# --------------------------------------------------
# Test 6
# Campaign statistics are calculated correctly
# --------------------------------------------------

def test_campaign_statistics():
    summary = CampaignSummary(
        campaign_id="CAMPAIGN-TEST",
        created_at_utc=(
            "2026-10-03T12:00:00+00:00"
        ),

        total_tests=4,
        passed_tests=3,
        failed_tests=1,

        overall_passed=False,

        # CampaignSummary.test_runs is tuple[dict, ...]
        # in the existing VETP implementation.
        test_runs=(
            {
                "run_id": "RUN-001",
                "test_id": "TC-001",
                "test_name": "Test One",
                "passed": True,
                "errors": [],
            },
            {
                "run_id": "RUN-002",
                "test_id": "TC-002",
                "test_name": "Test Two",
                "passed": True,
                "errors": [],
            },
            {
                "run_id": "RUN-003",
                "test_id": "TC-003",
                "test_name": "Test Three",
                "passed": True,
                "errors": [],
            },
            {
                "run_id": "RUN-004",
                "test_id": "TC-004",
                "test_name": "Test Four",
                "passed": False,
                "errors": [
                    "Controlled verification failure."
                ],
            },
        ),
    )

    pass_rate = calculate_campaign_pass_rate(
        summary
    )

    assert pass_rate == 75.0

    campaign_report = build_campaign_report(
        summary
    )

    assert "- Total Tests: 4" in campaign_report
    assert "- Passed: 3" in campaign_report
    assert "- Failed: 1" in campaign_report
    assert "- Pass Rate: 75.0%" in campaign_report
    assert "- Overall Result: FAIL" in campaign_report

    assert "RUN-001" in campaign_report
    assert "RUN-004" in campaign_report
    assert "| TC-001 | Test One | RUN-001 | PASS |" in campaign_report
    assert "| TC-004 | Test Four | RUN-004 | FAIL |" in campaign_report
    