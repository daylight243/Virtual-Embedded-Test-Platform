from pathlib import Path
from unittest.mock import Mock, patch
import hashlib
import pytest
from cloud_storage import (
    CloudStorageConfig,
    build_campaign_object_key,
    upload_campaign_artifact,
    verify_uploaded_campaign,
)
def config(): 
    return CloudStorageConfig("test-bucket", "ca-central-1")

def test_object_key():
    assert build_campaign_object_key("CAMP-TEST-001") == (
        "vetp/campaigns/campaign_CAMP-TEST-001.json"
    )
@pytest.mark.parametrize("bad", ["../bad", "bad/name", "", "a b"])

def test_object_key_rejects_unsafe_id(bad):
    with pytest.raises(ValueError):
        build_campaign_object_key(bad)

def test_missing_artifact(tmp_path: Path):
    result = upload_campaign_artifact(
        tmp_path / "missing.json", "CAMP-TEST", config()
    )
    assert result.success is False

def test_upload_with_mock_client(tmp_path: Path):
    artifact = tmp_path / "campaign_CAMP-TEST-001.json"
    content = b'{"campaign_id":"CAMP-TEST-001"}'
    artifact.write_bytes(content)
    client = Mock()
    with patch("cloud_storage.create_s3_client", return_value=client):
        result = upload_campaign_artifact(
            artifact, "CAMP-TEST-001", config()
        )
    assert result.success is True
    assert result.sha256 == hashlib.sha256(content).hexdigest()
    client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="vetp/campaigns/campaign_CAMP-TEST-001.json",
        Body=content,
        ContentType="application/json",
        IfNoneMatch="*",
    )

def test_remote_verification_with_mock_client(tmp_path: Path):
    artifact = tmp_path / "campaign_CAMP-TEST-001.json"
    artifact.write_bytes(b"same bytes")
    client = Mock()
    client.get_object.return_value = {
        "Body": Mock(read=Mock(return_value=b"same bytes"))
    }
    with patch("cloud_storage.create_s3_client", return_value=client):
        assert verify_uploaded_campaign(
            artifact, "CAMP-TEST-001", config()
        ) is True

def test_remote_verification_detects_mismatch(tmp_path: Path):
    artifact = tmp_path / "campaign_CAMP-TEST-001.json"
    artifact.write_bytes(b"local")
    client = Mock()
    client.get_object.return_value = {
        "Body": Mock(read=Mock(return_value=b"remote"))
    }
    with patch("cloud_storage.create_s3_client", return_value=client):
        assert verify_uploaded_campaign(
            artifact, "CAMP-TEST-001", config()
        ) is False