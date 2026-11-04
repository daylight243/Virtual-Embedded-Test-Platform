from dataclasses import dataclass
from pathlib import Path
import hashlib
import os
import re
import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)
@dataclass(frozen=True)
class CloudStorageConfig:
    bucket_name: str
    region_name: str
    profile_name: str | None = None

@dataclass(frozen=True)
class CloudStorageResult:
    campaign_id: str
    success: bool
    bucket_name: str
    object_key: str
    message: str
    sha256: str | None = None

def load_storage_config() -> CloudStorageConfig:
    bucket = os.getenv("VETP_S3_BUCKET", "").strip()
    region = os.getenv("VETP_AWS_REGION", "").strip()
    profile = os.getenv("VETP_AWS_PROFILE", "").strip() or None
    if not bucket:
        raise ValueError("VETP_S3_BUCKET is required.")
    if not region:
        raise ValueError("VETP_AWS_REGION is required.")
    return CloudStorageConfig(
        bucket_name=bucket,
        region_name=region,
        profile_name=profile,
    )

def build_campaign_object_key(campaign_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", campaign_id):
        raise ValueError("Invalid campaign ID for object key.")
    return f"vetp/campaigns/campaign_{campaign_id}.json"


def create_s3_client(config: CloudStorageConfig):
    session = boto3.Session(
        profile_name=config.profile_name,
        region_name=config.region_name,
    )
    return session.client("s3")

def upload_campaign_artifact(
    artifact_path: Path,
    campaign_id: str,
    config: CloudStorageConfig,
) -> CloudStorageResult:
    object_key = build_campaign_object_key(campaign_id)
    if not artifact_path.is_file():
        return CloudStorageResult(
            campaign_id=campaign_id,
            success=False,
            bucket_name=config.bucket_name,
            object_key=object_key,
            message="Local campaign artifact not found.",
        )
    content = artifact_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    try:
        client = create_s3_client(config)
        client.put_object(
            Bucket=config.bucket_name,
            Key=object_key,
            Body=content,
            ContentType="application/json",
            IfNoneMatch="*",
        )
    except (BotoCoreError, ClientError, OSError) as exc:
        return CloudStorageResult(
            campaign_id=campaign_id,
            success=False,
            bucket_name=config.bucket_name,
            object_key=object_key,
            message=f"S3 upload failed: {exc}",
            sha256=digest,
        )
    return CloudStorageResult(
        campaign_id=campaign_id,
        success=True,
        bucket_name=config.bucket_name,
        object_key=object_key,
        message="Campaign uploaded to S3.",
        sha256=digest,
    )

def verify_uploaded_campaign(
    artifact_path: Path,
    campaign_id: str,
    config: CloudStorageConfig,
) -> bool:
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)
    object_key = build_campaign_object_key(campaign_id)
    local_hash = hashlib.sha256(
        artifact_path.read_bytes()
    ).hexdigest()
    client = create_s3_client(config)
    response = client.get_object(
        Bucket=config.bucket_name,
        Key=object_key,
    )
    try: remote_bytes = response["Body"].read()
    finally:
        response["Body"].close()
    remote_hash = hashlib.sha256(remote_bytes).hexdigest()
    return local_hash == remote_hash

