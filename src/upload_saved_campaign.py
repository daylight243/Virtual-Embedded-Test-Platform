import argparse
import json
from pathlib import Path
from botocore.exceptions import BotoCoreError, ClientError
from cloud_campaign import (
    CloudCampaignRun,
    CloudCampaignSummary,
    validate_cloud_campaign_summary,
)
from cloud_storage import (
    load_storage_config,
    upload_campaign_artifact,
    verify_uploaded_campaign,
)
def read_campaign(path: Path) -> CloudCampaignSummary:
    payload = json.loads(path.read_text(encoding="utf-8"))
    runs = tuple(
        CloudCampaignRun(**run) for run in payload["runs"]
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
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    path = args.artifact
    summary = read_campaign(path)
    expected = f"campaign_{summary.campaign_id}.json"
    
    if path.name != expected:
        raise ValueError(f"Expected artifact filename: {expected}")
    
    config = load_storage_config()
    
    print("Engineering PASS:", summary.overall_passed)
    print("Campaign:", summary.campaign_id)
    
    result = upload_campaign_artifact(
        path, summary.campaign_id, config
    )
    
    print("Upload success:", result.success)
    print("Upload message:", result.message)
    print("Bucket:", result.bucket_name)
    print("Object key:", result.object_key)
    print("Local SHA-256:", result.sha256)
    
    if not result.success:
        raise SystemExit(1)
    
    try:
        verified = verify_uploaded_campaign(
            path, summary.campaign_id, config
        )
    
    except (BotoCoreError, ClientError, OSError) as exc:
        print("Remote verification failed:", exc)
        raise SystemExit(1)
    print("Remote artifact verified:", verified)
    if not verified:
        raise SystemExit(1)

if __name__ == "__main__":
    main()