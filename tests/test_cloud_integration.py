import json

import pytest

from cloud_integration import (
    CloudRunSummary,
    build_cloud_run_summary,
    cloud_summary_to_json,
    load_cloud_config,
    validate_cloud_run_summary,
    CloudConfig,
    publish_run_summary,
)

from test_logging import TestRunLog


def build_test_log(
    passed: bool = True,
) -> TestRunLog:

    return TestRunLog(
        run_id="TC-005_TEST_RUN",
        test_id="TC-005",
        test_name="Overcurrent Shutdown",
        description=(
            "Controlled cloud integration test run."
        ),
        started_at_utc=(
            "2026-10-14T20:00:00Z"
        ),
        measurements=(),
        hdl_inputs=(),
        expected_results=(),
        actual_results=(),
        verification_results=(),
        passed=passed,
        errors=(),
    )

def test_cloud_summary_preserves_identity():

    test_log = build_test_log()

    summary = build_cloud_run_summary(
        test_log=test_log,
        device_id="PWR-001",
    )

    assert (
        summary.run_id
        == test_log.run_id
    )

    assert (
        summary.test_id
        == test_log.test_id
    )

    assert (
        summary.test_name
        == test_log.test_name
    )


def test_cloud_summary_preserves_device_identity():

    test_log = build_test_log()

    expected_device_id = "PWR-001"

    summary = build_cloud_run_summary(
        test_log=test_log,
        device_id=expected_device_id,
    )

    assert (
        summary.device_id
        == expected_device_id
    )


def test_cloud_summary_preserves_pass_result():

    test_log = build_test_log(
        passed=True
    )

    summary = build_cloud_run_summary(
        test_log=test_log,
        device_id="PWR-001",
    )

    assert summary.passed is True


def test_cloud_summary_preserves_fail_result():

    test_log = build_test_log(
        passed=False
    )

    summary = build_cloud_run_summary(
        test_log=test_log,
        device_id="PWR-001",
    )

    assert summary.passed is False


def test_empty_run_id_fails_validation():

    summary = CloudRunSummary(
        schema_version="1.0",
        run_id="",
        device_id="PWR-001",
        test_id="TC-005",
        test_name="Overcurrent Shutdown",
        started_at_utc=(
            "2026-10-14T20:00:00Z"
        ),
        passed=True,
    )

    with pytest.raises(
        ValueError,
        match="run_id must not be empty",
    ):

        validate_cloud_run_summary(
            summary
        )


def test_cloud_json_contains_schema_version():

    test_log = build_test_log()

    summary = build_cloud_run_summary(
        test_log=test_log,
        device_id="PWR-001",
    )

    payload = cloud_summary_to_json(
        summary
    )

    payload_data = json.loads(
        payload
    )

    assert (
        payload_data["schema_version"]
        == "1.0"
    )


def test_default_cloud_mode(
    monkeypatch,
):

    monkeypatch.delenv(
        "VETP_CLOUD_MODE",
        raising=False,
    )

    monkeypatch.delenv(
        "VETP_CLOUD_ENDPOINT",
        raising=False,
    )

    monkeypatch.delenv(
        "VETP_CLOUD_API_KEY",
        raising=False,
    )

    config = load_cloud_config()

    assert config.mode == "local"

    assert config.endpoint is None

    assert config.api_key is None


def test_cloud_mode_from_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "VETP_CLOUD_MODE",
        "remote",
    )

    config = load_cloud_config()

    assert config.mode == "remote"


def test_cloud_endpoint_from_environment(
    monkeypatch,
):

    expected_endpoint = (
        "https://example.invalid/vetp"
    )

    monkeypatch.setenv(
        "VETP_CLOUD_ENDPOINT",
        expected_endpoint,
    )

    config = load_cloud_config()

    assert (
        config.endpoint
        == expected_endpoint
    )


def test_cloud_api_key_from_environment(
    monkeypatch,
):

    expected_api_key = (
        "test-key-not-a-real-secret"
    )

    monkeypatch.setenv(
        "VETP_CLOUD_API_KEY",
        expected_api_key,
    )

    config = load_cloud_config()

    assert (
        config.api_key
        == expected_api_key
    )

def build_publish_test_summary() -> CloudRunSummary:
    """
    Controlled unit-test fixture.
    Not a genuine engineering execution.
    """
    return CloudRunSummary(
        schema_version="1.0",
        run_id="UNIT-TEST-RUN-001",
        device_id="PWR-001",
        test_id="TC-005",
        test_name="Overcurrent Shutdown",
        started_at_utc="2026-10-20T00:00:00Z",
        passed=True,
    )


def build_publish_test_config(
    mode: str,
    endpoint: str | None = None,
) -> CloudConfig:

    return CloudConfig(
        mode=mode,
        endpoint=endpoint,
        api_key=None,
        timeout_seconds=5.0,
    )


def test_local_publication_still_works(
    monkeypatch,
    tmp_path,
):

    import cloud_integration

    monkeypatch.setattr(
        cloud_integration,
        "CLOUD_OUTBOX_DIR",
        tmp_path / "cloud_outbox",
    )

    summary = build_publish_test_summary()

    config = build_publish_test_config(
        mode="local",
    )

    result = publish_run_summary(
        summary,
        config,
    )

    assert result.success is True
    assert result.run_id == summary.run_id
    assert result.status_code is None

    output_path = (
        tmp_path
        / "cloud_outbox"
        / "run_UNIT-TEST-RUN-001.json"
    )

    assert output_path.exists()

    import json

    saved_payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert saved_payload["run_id"] == summary.run_id
    assert saved_payload["passed"] is True


def test_unsupported_cloud_mode():

    summary = build_publish_test_summary()

    config = build_publish_test_config(
        mode="something_else",
    )

    result = publish_run_summary(
        summary,
        config,
    )

    assert result.success is False
    assert result.run_id == summary.run_id
    assert result.status_code is None
    assert "Unsupported cloud mode" in result.message


def test_missing_api_endpoint():

    summary = build_publish_test_summary()

    config = build_publish_test_config(
        mode="api",
        endpoint=None,
    )

    result = publish_run_summary(
        summary,
        config,
    )

    assert result.success is False
    assert result.run_id == summary.run_id
    assert result.status_code is None
    assert "not configured" in result.message


def test_publication_preserves_run_identity(
    monkeypatch,
    tmp_path,
):

    import cloud_integration

    monkeypatch.setattr(
        cloud_integration,
        "CLOUD_OUTBOX_DIR",
        tmp_path / "cloud_outbox",
    )

    summary = build_publish_test_summary()

    config = build_publish_test_config(
        mode="local",
    )

    result = publish_run_summary(
        summary,
        config,
    )

    assert result.run_id == summary.run_id  