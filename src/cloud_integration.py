from dataclasses import dataclass, asdict
from pathlib import Path

import json
import os
import re

from test_logging import TestRunLog


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CLOUD_OUTBOX_DIR = (
    PROJECT_ROOT
    / "build"
    / "cloud_outbox"
)


# ---------------------------------------------------------
# Cloud run summary
# ---------------------------------------------------------

@dataclass(frozen=True)
class CloudRunSummary:

    schema_version: str

    run_id: str

    device_id: str

    test_id: str

    test_name: str

    started_at_utc: str

    passed: bool


# ---------------------------------------------------------
# Cloud configuration
# ---------------------------------------------------------

@dataclass(frozen=True)
class CloudConfig:

    mode: str

    endpoint: str | None

    api_key: str | None


# ---------------------------------------------------------
# Build a cloud summary from a completed VETP run
# ---------------------------------------------------------

def build_cloud_run_summary(
    test_log: TestRunLog,
    device_id: str,
) -> CloudRunSummary:

    return CloudRunSummary(
        schema_version="1.0",
        run_id=test_log.run_id,
        device_id=device_id,
        test_id=test_log.test_id,
        test_name=test_log.test_name,
        started_at_utc=(
            test_log.started_at_utc
        ),
        passed=test_log.passed,
    )


# ---------------------------------------------------------
# Convert the summary to a dictionary
# ---------------------------------------------------------

def cloud_summary_to_dict(
    summary: CloudRunSummary,
) -> dict:

    return asdict(summary)


# ---------------------------------------------------------
# Validate the cloud summary
# ---------------------------------------------------------

def validate_cloud_run_summary(
    summary: CloudRunSummary,
) -> None:

    if not summary.schema_version:
        raise ValueError(
            "schema_version must not be empty."
        )

    if not summary.run_id:
        raise ValueError(
            "run_id must not be empty."
        )

    if not summary.device_id:
        raise ValueError(
            "device_id must not be empty."
        )

    if not summary.test_id:
        raise ValueError(
            "test_id must not be empty."
        )

    if not summary.test_name:
        raise ValueError(
            "test_name must not be empty."
        )

    if not summary.started_at_utc:
        raise ValueError(
            "started_at_utc must not be empty."
        )


# ---------------------------------------------------------
# Convert the summary to JSON
# ---------------------------------------------------------

def cloud_summary_to_json(
    summary: CloudRunSummary,
) -> str:

    validate_cloud_run_summary(
        summary
    )

    return json.dumps(
        asdict(summary),
        indent=2,
    )


# ---------------------------------------------------------
# Load cloud configuration
# ---------------------------------------------------------

def load_cloud_config() -> CloudConfig:

    mode = os.getenv(
        "VETP_CLOUD_MODE",
        "local",
    )

    endpoint = os.getenv(
        "VETP_CLOUD_ENDPOINT"
    )

    api_key = os.getenv(
        "VETP_CLOUD_API_KEY"
    )

    return CloudConfig(
        mode=mode,
        endpoint=endpoint,
        api_key=api_key,
    )


# ---------------------------------------------------------
# Ensure the local cloud outbox exists
# ---------------------------------------------------------

def ensure_cloud_outbox() -> None:

    CLOUD_OUTBOX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ---------------------------------------------------------
# Make a value safe for use in a filename
# ---------------------------------------------------------

def safe_filename_part(
    value: str,
) -> str:

    return re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        value,
    )


# ---------------------------------------------------------
# Save a cloud-ready payload locally
# ---------------------------------------------------------

def save_cloud_payload_locally(
    summary: CloudRunSummary,
) -> Path:

    ensure_cloud_outbox()

    payload = cloud_summary_to_json(
        summary
    )

    safe_run_id = safe_filename_part(
        summary.run_id
    )

    output_path = (
        CLOUD_OUTBOX_DIR
        / f"run_{safe_run_id}.json"
    )

    output_path.write_text(
        payload,
        encoding="utf-8",
    )

    return output_path

@dataclass(frozen=True)
class CloudPublishResult:

    run_id: str

    success: bool

    destination: str

    message: str


def publish_run_summary_locally(
    summary: CloudRunSummary,
) -> CloudPublishResult:

    output_path = (
        save_cloud_payload_locally(
            summary
        )
    )

    return CloudPublishResult(
        run_id=summary.run_id,
        success=True,
        destination=str(
            output_path
        ),
        message=(
            "Cloud payload prepared "
            "in local outbox."
        ),
    )

