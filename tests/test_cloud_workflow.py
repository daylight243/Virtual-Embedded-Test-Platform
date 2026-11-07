from pathlib import Path

from cloud_workflow import (
    CloudWorkflowResult,
    publication_status,
)


def make_result(
    *,
    engineering_passed=True,
    publication_success=True,
    publication_verified=None,
    mode="api",
):
    return CloudWorkflowResult(
        campaign_id="CAMP-TEST",
        engineering_passed=engineering_passed,
        publication_success=publication_success,
        publication_verified=publication_verified,
        publication_mode=mode,
        artifact_path=Path("test.json"),
        message="Test result.",
    )


def test_local_status():
    result = make_result(
        mode="local"
    )

    assert publication_status(result) == "LOCAL_ONLY"


def test_published_status():
    result = make_result(
        mode="api"
    )

    assert publication_status(result) == "PUBLISHED"


def test_verified_status():
    result = make_result(
        mode="s3",
        publication_verified=True,
    )

    assert publication_status(result) == "VERIFIED"


def test_failed_status():
    result = make_result(
        publication_success=False,
    )

    assert publication_status(result) == "FAILED"


def test_unverified_status():
    result = make_result(
        mode="s3",
        publication_verified=False,
    )

    assert publication_status(result) == "UNVERIFIED"


def test_engineering_failure_is_independent():
    result = make_result(
        engineering_passed=False,
        publication_success=True,
        publication_verified=True,
        mode="s3",
    )

    assert result.engineering_passed is False
    assert publication_status(result) == "VERIFIED"

    