from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from test_logging import TestRunLog
from dataclasses import asdict
import json

from pathlib import Path
import re
import sqlite3

PROJECT_ROOT = (
    Path(__file__).resolve().parents[1]
)

CAMPAIGN_OUTBOX_DIR = (
    PROJECT_ROOT
    / "build"
    / "cloud_outbox"
    / "campaigns"
)


@dataclass(frozen=True)
class CloudCampaignRun:
    run_id: str
    test_id: str
    passed: bool


@dataclass(frozen=True)
class CloudCampaignSummary:
    schema_version: str
    campaign_id: str
    created_at_utc: str
    device_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate_percent: float
    overall_passed: bool
    runs: tuple[CloudCampaignRun, ...]

def build_cloud_campaign_summary(
    test_logs: tuple[TestRunLog, ...],
    device_id: str,
    campaign_id: str | None = None,
) -> CloudCampaignSummary:

    if not test_logs:
        raise ValueError(
            "Cannot build a campaign "
            "from zero test runs."
        )

    if not device_id.strip():
        raise ValueError(
            "device_id cannot be empty."
        )

    run_ids = [
        log.run_id
        for log in test_logs
    ]

    if len(run_ids) != len(set(run_ids)):
        raise ValueError(
            "Campaign contains duplicate run IDs."
        )

    if campaign_id is None:
        campaign_id = (
            f"CAMP-{uuid4().hex[:12]}"
        )

    runs = tuple(
        CloudCampaignRun(
            run_id=log.run_id,
            test_id=log.test_id,
            passed=log.passed,
        )
        for log in test_logs
    )

    total_tests = len(runs)

    passed_tests = sum(
        1 for run in runs
        if run.passed
    )

    failed_tests = (
        total_tests - passed_tests
    )

    pass_rate = (
        passed_tests / total_tests
    ) * 100.0

    return CloudCampaignSummary(
        schema_version="1.0",
        campaign_id=campaign_id,
        created_at_utc=(
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        device_id=device_id,
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        pass_rate_percent=round(
            pass_rate, 2
        ),
        overall_passed=(
            failed_tests == 0
        ),
        runs=runs,
    )

def validate_cloud_campaign_summary(
    summary: CloudCampaignSummary,
) -> None:

    if summary.schema_version != "1.0":
        raise ValueError(
            "Unsupported campaign schema version."
        )

    if not summary.campaign_id.strip():
        raise ValueError(
            "Missing campaign ID."
        )

    if not summary.device_id.strip():
        raise ValueError(
            "Missing device ID."
        )

    if summary.total_tests <= 0:
        raise ValueError(
            "Campaign must contain at least one run."
        )

    if summary.total_tests != len(summary.runs):
        raise ValueError(
            "Total test count does not match runs."
        )

    passed = sum(
        1 for run in summary.runs
        if run.passed
    )

    failed = (
        len(summary.runs) - passed
    )

    if summary.passed_tests != passed:
        raise ValueError(
            "Incorrect passed-test count."
        )

    if summary.failed_tests != failed:
        raise ValueError(
            "Incorrect failed-test count."
        )

    if summary.overall_passed != (
        failed == 0
    ):
        raise ValueError(
            "Incorrect overall campaign result."
        )

    expected_rate = round(
        passed / len(summary.runs) * 100,
        2,
    )

    if abs(
        summary.pass_rate_percent
        - expected_rate
    ) > 0.001:
        raise ValueError(
            "Incorrect campaign pass rate."
        )

    ids = [
        run.run_id
        for run in summary.runs
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate run IDs."
        )

    for run in summary.runs:
        if (
            not run.run_id.strip()
            or not run.test_id.strip()
            or type(run.passed) is not bool
        ):
            raise ValueError(
                "Invalid campaign run entry."
            )

def cloud_campaign_to_json(
    summary: CloudCampaignSummary,
) -> str:

    validate_cloud_campaign_summary(
        summary
    )

    return json.dumps(
        asdict(summary),
        indent=2,
        allow_nan=False,
    )


def save_campaign_to_outbox(
    summary: CloudCampaignSummary,
) -> Path:

    json_text = cloud_campaign_to_json(
        summary
    )

    CAMPAIGN_OUTBOX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_id = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        summary.campaign_id,
    )

    path = (
        CAMPAIGN_OUTBOX_DIR
        / f"campaign_{safe_id}.json"
    )

    if path.exists():
        raise FileExistsError(
            f"Campaign artifact already exists: {path}"
        )

    path.write_text(
        json_text,
        encoding="utf-8",
    )

    return path

def verify_campaign_against_database(
    connection: sqlite3.Connection,
    summary: CloudCampaignSummary,
) -> None:

    validate_cloud_campaign_summary(
        summary
    )

    for run in summary.runs:

        row = connection.execute(
            """
            SELECT
                device_id,
                test_id,
                passed
            FROM test_runs
            WHERE run_id = ?;
            """,
            (run.run_id,),
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Missing SQLite run: {run.run_id}"
            )

        stored_device_id = row[0]
        stored_test_id = row[1]
        stored_passed = bool(row[2])

        if stored_device_id != summary.device_id:
            raise ValueError(
                f"Device mismatch for run: {run.run_id}"
            )

        if stored_test_id != run.test_id:
            raise ValueError(
                f"Test ID mismatch for run: {run.run_id}"
            )

        if stored_passed != run.passed:
            raise ValueError(
                f"PASS/FAIL mismatch for run: {run.run_id}"
            )

