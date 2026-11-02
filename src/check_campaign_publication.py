import json
import sys

from pathlib import Path

from cloud_campaign import (
    CloudCampaignRun,
    CloudCampaignSummary,
    validate_cloud_campaign_summary,
)

from cloud_campaign_publisher import (
    publish_campaign_http,
)

from cloud_integration import (
    load_cloud_config,
)


def load_saved_campaign(
    path: Path,
) -> CloudCampaignSummary:

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    runs = tuple(
        CloudCampaignRun(
            run_id=run["run_id"],
            test_id=run["test_id"],
            passed=run["passed"],
        )
        for run in payload["runs"]
    )

    summary = CloudCampaignSummary(
        schema_version=payload["schema_version"],
        campaign_id=payload["campaign_id"],
        created_at_utc=payload["created_at_utc"],
        device_id=payload["device_id"],
        total_tests=payload["total_tests"],
        passed_tests=payload["passed_tests"],
        failed_tests=payload["failed_tests"],
        pass_rate_percent=payload["pass_rate_percent"],
        overall_passed=payload["overall_passed"],
        runs=runs,
    )

    validate_cloud_campaign_summary(summary)

    return summary


def main() -> None:

    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python "
            "src/check_campaign_publication.py "
            "<campaign-json-path>"
        )

    campaign_path = Path(sys.argv[1])

    summary = load_saved_campaign(
        campaign_path
    )

    config = load_cloud_config()

    print("Campaign:", summary.campaign_id)
    print("Engineering PASS:", summary.overall_passed)

    result = publish_campaign_http(
        summary,
        config,
    )

    print("Publication success:", result.success)
    print("HTTP status:", result.status_code)
    print("Message:", result.message)


if __name__ == "__main__":
    main()