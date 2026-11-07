from dataclasses import dataclass
from pathlib import Path

import sqlite3
from test_logging import TestRunLog
from cloud_campaign import (
    build_cloud_campaign_summary,
    validate_cloud_campaign_summary,
    verify_campaign_against_database,
    save_campaign_to_outbox,
)
from cloud_integration import CloudConfig
from cloud_campaign_publisher import publish_campaign_http
from cloud_storage import (
    load_storage_config,
    upload_campaign_artifact,
    verify_uploaded_campaign,
)
@dataclass(frozen=True)
class CloudWorkflowResult:
    campaign_id: str
    engineering_passed: bool
    publication_success: bool
    publication_verified: bool | None
    publication_mode: str
    artifact_path: Path
    message: str

def publish_completed_campaign(
    *,
    test_logs: tuple[TestRunLog, ...],
    device_id: str,
    connection: sqlite3.Connection,
    config: CloudConfig,
    campaign_id: str | None = None,
) -> CloudWorkflowResult:
    
    summary = build_cloud_campaign_summary(
        test_logs=test_logs,
        device_id=device_id,
        campaign_id=campaign_id,
    )
    
    validate_cloud_campaign_summary(summary)
    verify_campaign_against_database(connection, summary)
    artifact_path = save_campaign_to_outbox(summary)
    
    if config.mode == "local":
        return CloudWorkflowResult(
            campaign_id=summary.campaign_id,
            engineering_passed=summary.overall_passed,
            publication_success=True,
            publication_verified=None,
            publication_mode="local",
            artifact_path=artifact_path,
            message="Campaign prepared in local outbox.",
        )
    
    if config.mode == "api":
        try:
            result = publish_campaign_http(summary, config)
            success = bool(result.success)
            message = result.message
        
        except Exception as exc:
            success = False
            message = f"API publication failed: {exc}"
        
        return CloudWorkflowResult(
            campaign_id=summary.campaign_id,
            engineering_passed=summary.overall_passed,
            publication_success=success,
              publication_verified=None,
            publication_mode="api",
            artifact_path=artifact_path,
            message=message,
        )
    
    if config.mode == "s3":
        try:
            storage_config = load_storage_config()
            result = upload_campaign_artifact(
                artifact_path=artifact_path,
                campaign_id=summary.campaign_id,
                config=storage_config,
            )
        except Exception as exc:
            return CloudWorkflowResult(
                campaign_id=summary.campaign_id,
                engineering_passed=summary.overall_passed,
                publication_success=False,
                publication_verified=None,
                publication_mode="s3",
                artifact_path=artifact_path,
                message=f"S3 publication failed: {exc}",
            )
        if not result.success:
            return CloudWorkflowResult(
                campaign_id=summary.campaign_id,
                engineering_passed=summary.overall_passed,
                publication_success=False,
                publication_verified=None,
                publication_mode="s3",
                artifact_path=artifact_path,
                message=result.message,
            )
        try:
            verified = verify_uploaded_campaign(
                artifact_path=artifact_path,
                campaign_id=summary.campaign_id,
                config=storage_config,
            )
            message = (
                "S3 artifact verified."
                if verified else "S3 uploaded; SHA-256 mismatch."
            )
        except Exception as exc:
            verified = False
            message = f"S3 uploaded; verification unavailable: {exc}"
        return CloudWorkflowResult(
            campaign_id=summary.campaign_id,
            engineering_passed=summary.overall_passed,
            publication_success=True,
            publication_verified=verified,
            publication_mode="s3",
            artifact_path=artifact_path,
            message=message,
        )
    return CloudWorkflowResult(
        campaign_id=summary.campaign_id,
        engineering_passed=summary.overall_passed,
        publication_success=False,
        publication_verified=None,
        publication_mode=config.mode,
        artifact_path=artifact_path,
        message=f"Unsupported cloud mode: {config.mode}",
    )

def publication_status(result: CloudWorkflowResult) -> str:
    if result.publication_mode == "local":
        return "LOCAL_ONLY"
    if not result.publication_success:
        return "FAILED"
    if result.publication_verified is True:
        return "VERIFIED"
    if result.publication_verified is False:
        return "UNVERIFIED"
    return "PUBLISHED"


