import json
import re

from pathlib import Path
from datetime import datetime, timezone

from database import connect_database

from test_logging import TestRunLog

from database_queries import (
    get_fault_events_for_run,
)



PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "build" / "reports"


def ensure_reports_directory() -> None:
    """Create the reports directory if it does not exist."""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )




def current_utc_timestamp() -> str:
    """Return the current UTC date and time."""

    return datetime.now(
        timezone.utc
    ).isoformat()

def display_value(value) -> str:

    if value is None:
        return "N/A"

    return str(value)

def build_fpga_timeline(
    actual_results: tuple[dict, ...],
) -> str:

    lines = [
        "| Time | State | Fault | Alarm | Shutdown |",
        "|---|---:|---:|---:|---:|",
    ]

    for result in actual_results:

        timestamp = display_value(
            result.get("timestamp")
        )

        state = display_value(
            result.get("state_code")
        )

        fault = display_value(
            result.get("fault_code")
        )

        alarm = display_value(
            result.get("alarm")
        )

        shutdown = display_value(
            result.get("shutdown")
        )

        lines.append(
            f"| {timestamp} "
            f"| {state} "
            f"| {fault} "
            f"| {alarm} "
            f"| {shutdown} |"
        )

    if not actual_results:
        return "No FPGA output samples were recorded."

    return "\n".join(lines)

def build_fault_event_table(
    fault_events,
) -> str:

    # A test without injected faults is valid.
    # Do not invent a fault event.
    if not fault_events:
        return "No fault injections were recorded."

    lines = [
        "| Fault | Start | Duration |",
        "|---|---:|---:|",
    ]

    for event in fault_events:

        lines.append(
            f"| {event['fault_type']} "
            f"| {event['start_timestamp']} "
            f"| {event['duration']} |"
        )

    return "\n".join(lines)


def format_evidence(
    records,
) -> str:

    if not records:
        return "No records available."

    formatted = json.dumps(
        list(records),
        indent=2,
    )

    return (
        "```json\n"
        + formatted
        + "\n```"
    )    

def build_test_report(
    test_log: TestRunLog,
    fault_events=(),
) -> str:

    # --------------------------------------------------
    # Engineering verification result
    # --------------------------------------------------

    result = (
        "PASS"
        if test_log.passed
        else "FAIL"
    )

    # --------------------------------------------------
    # Report-generation timestamp
    # --------------------------------------------------

    generated_at = current_utc_timestamp()

    # --------------------------------------------------
    # FPGA output timeline
    # --------------------------------------------------

    timeline = build_fpga_timeline(
        test_log.actual_results
    )

    # --------------------------------------------------
    # Fault-injection evidence
    # --------------------------------------------------

    fault_table = build_fault_event_table(
        fault_events
    )

    # --------------------------------------------------
    # Expected-result evidence
    # --------------------------------------------------

    expected = format_evidence(
        test_log.expected_results
    )

    # --------------------------------------------------
    # Verification evidence
    # --------------------------------------------------

    verification = format_evidence(
        test_log.verification_results
    )

    # --------------------------------------------------
    # Recorded errors
    # --------------------------------------------------

    errors = format_evidence(
        test_log.errors
    )

    # --------------------------------------------------
    # Measurement evidence
    # --------------------------------------------------

    measurements = format_evidence(
        test_log.measurements
    )

    # --------------------------------------------------
    # Markdown engineering report
    # --------------------------------------------------

    return f"""# VETP Engineering Test Report

## 1. Test Information

- Run ID: {test_log.run_id}
- Test ID: {test_log.test_id}
- Test Name: {test_log.test_name}
- Started: {test_log.started_at_utc}
- Report Generated: {generated_at}

## 2. Test Objective

{test_log.description}

## 3. Verification Summary

**Result: {result}**

## 4. Fault Injection Evidence

{fault_table}

## 5. FPGA Output Timeline

{timeline}

## 6. Expected Results

{expected}

## 7. Verification Details

{verification}

## 8. Recorded Errors

{errors}

## 9. Measurements

{measurements}

## 10. Evidence References

- Run ID: {test_log.run_id}
- Persistent database: build/vetp.db
- Detailed evidence: corresponding JSON test log

"""

def safe_filename_part(value: str) -> str:

    return re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        value,
    )

def save_test_report(
    test_log: TestRunLog,
    report_text: str,
) -> Path:

    
    ensure_reports_directory()

    
    safe_run_id = safe_filename_part(
        test_log.run_id
    )

    report_path = (
        REPORTS_DIR
        / f"test_{safe_run_id}.md"
    )

    
    report_path.write_text(
        report_text,
        encoding="utf-8",
    )

    return report_path

def generate_test_report(
    test_log: TestRunLog,
) -> Path:

    
    connection = connect_database()

    try:
      
        fault_events = get_fault_events_for_run(
            connection,
            test_log.run_id,
        )

        
        report_text = build_test_report(
            test_log,
            fault_events,
        )

    
        report_path = save_test_report(
            test_log,
            report_text,
        )

        print(
            f"Report saved: {report_path}"
        )

        return report_path

    finally:
        connection.close()

def calculate_campaign_pass_rate(
    summary,
) -> float:

    
    if summary.total_tests == 0:
        return 0.0

    
    return (
        summary.passed_tests
        / summary.total_tests
        * 100.0
    )     

def build_campaign_report(
    summary,
) -> str:

    generated_at = current_utc_timestamp()

    pass_rate = calculate_campaign_pass_rate(
        summary
    )

    overall = (
        "PASS"
        if summary.overall_passed
        else "FAIL"
    )

    lines = [
        "# VETP Engineering Campaign Report",
        "",
        "## Campaign Information",
        "",
        f"- Campaign ID: {summary.campaign_id}",
        f"- Created: {summary.created_at_utc}",
        f"- Report Generated: {generated_at}",
        "",
        "## Campaign Summary",
        "",
        f"- Total Tests: {summary.total_tests}",
        f"- Passed: {summary.passed_tests}",
        f"- Failed: {summary.failed_tests}",
        f"- Pass Rate: {pass_rate:.1f}%",
        f"- Overall Result: {overall}",
        "",
        "## Individual Test Results",
        "",
        "| Test ID | Test Name | Run ID | Result |",
        "|---|---|---|---|",
    ]

    for test_run in summary.test_runs:

        result = (
            "PASS"
            if test_run["passed"]
            else "FAIL"
        )

        lines.append(
            f"| {test_run['test_id']} "
            f"| {test_run['test_name']} "
            f"| {test_run['run_id']} "
            f"| {result} |"
        )

    return "\n".join(lines) + "\n"

def save_campaign_report(
    summary,
    report_text: str,
) -> Path:

    ensure_reports_directory()

    safe_campaign_id = safe_filename_part(
        summary.campaign_id
    )

    report_path = (
        REPORTS_DIR
        / f"campaign_{safe_campaign_id}.md"
    )

    report_path.write_text(
        report_text,
        encoding="utf-8",
    )

    return report_path

