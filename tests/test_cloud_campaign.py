from dataclasses import replace

import pytest

from cloud_campaign import (
    CloudCampaignRun,
    CloudCampaignSummary,
    validate_cloud_campaign_summary,
    cloud_campaign_to_json,
)


# =========================================================
# Test fixture
# =========================================================

def make_valid_summary() -> CloudCampaignSummary:

    return CloudCampaignSummary(
        schema_version="1.0",
        campaign_id="CAMP-TEST",
        created_at_utc="2026-01-01T00:00:00Z",
        device_id="DEVICE-TEST",
        total_tests=2,
        passed_tests=1,
        failed_tests=1,
        pass_rate_percent=50.0,
        overall_passed=False,
        runs=(
            CloudCampaignRun(
                run_id="RUN-TEST-1",
                test_id="TC-001",
                passed=True,
            ),
            CloudCampaignRun(
                run_id="RUN-TEST-2",
                test_id="TC-002",
                passed=False,
            ),
        ),
    )


# =========================================================
# Test 1 — Valid campaign is accepted
# =========================================================

def test_valid_campaign():

    summary = make_valid_summary()

    validate_cloud_campaign_summary(
        summary
    )


# =========================================================
# Test 2 — Empty campaign is rejected
# =========================================================

def test_empty_campaign_rejected():

    summary = replace(
        make_valid_summary(),
        total_tests=0,
        passed_tests=0,
        failed_tests=0,
        pass_rate_percent=0.0,
        overall_passed=True,
        runs=(),
    )

    with pytest.raises(ValueError):
        validate_cloud_campaign_summary(
            summary
        )


# =========================================================
# Test 3 — Incorrect passed count is rejected
# =========================================================

def test_incorrect_passed_count():

    summary = replace(
        make_valid_summary(),
        passed_tests=2,
    )

    with pytest.raises(
        ValueError,
        match="Incorrect passed-test count",
    ):
        validate_cloud_campaign_summary(
            summary
        )


# =========================================================
# Test 4 — Incorrect failed count is rejected
# =========================================================

def test_incorrect_failed_count():

    summary = replace(
        make_valid_summary(),
        failed_tests=0,
    )

    with pytest.raises(
        ValueError,
        match="Incorrect failed-test count",
    ):
        validate_cloud_campaign_summary(
            summary
        )


# =========================================================
# Test 5 — Duplicate run IDs are rejected
# =========================================================

def test_duplicate_run_ids():

    summary = make_valid_summary()

    duplicate_runs = (
        CloudCampaignRun(
            run_id="RUN-TEST-1",
            test_id="TC-001",
            passed=True,
        ),
        CloudCampaignRun(
            run_id="RUN-TEST-1",
            test_id="TC-002",
            passed=False,
        ),
    )

    summary = replace(
        summary,
        runs=duplicate_runs,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate run IDs",
    ):
        validate_cloud_campaign_summary(
            summary
        )


# =========================================================
# Test 6 — Incorrect overall result is rejected
# =========================================================

def test_incorrect_overall_status():

    summary = replace(
        make_valid_summary(),
        overall_passed=True,
    )

    with pytest.raises(
        ValueError,
        match="Incorrect overall campaign result",
    ):
        validate_cloud_campaign_summary(
            summary
        )


# =========================================================
# Test 7 — Incorrect pass rate is rejected
# =========================================================

def test_incorrect_pass_rate():

    summary = replace(
        make_valid_summary(),
        pass_rate_percent=100.0,
    )

    with pytest.raises(
        ValueError,
        match="Incorrect campaign pass rate",
    ):
        validate_cloud_campaign_summary(
            summary
        )
        


# =========================================================
# Test 8 — Failed engineering campaign is valid
# =========================================================

def test_failed_campaign_is_valid():

    summary = make_valid_summary()

    assert summary.overall_passed is False
    assert summary.failed_tests == 1

    validate_cloud_campaign_summary(
        summary
    )


# =========================================================
# Test 9 — JSON serialization preserves identity
# =========================================================

def test_campaign_json_preserves_identity():

    import json

    summary = make_valid_summary()

    json_text = cloud_campaign_to_json(
        summary
    )

    payload = json.loads(
        json_text
    )

    assert payload["campaign_id"] == "CAMP-TEST"
    assert payload["device_id"] == "DEVICE-TEST"
    assert payload["total_tests"] == 2
    assert payload["passed_tests"] == 1
    assert payload["failed_tests"] == 1
    assert payload["overall_passed"] is False

    assert payload["runs"][0]["run_id"] == "RUN-TEST-1"
    assert payload["runs"][1]["run_id"] == "RUN-TEST-2"
    