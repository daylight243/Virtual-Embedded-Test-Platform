from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import json
import os

from cloud_campaign import (
    CloudCampaignSummary,
    build_cloud_campaign_summary,
    cloud_campaign_to_json,
    save_campaign_to_outbox,
)

from cloud_integration import (
    CloudConfig,
    CloudPublishResult,
)

from test_logging import TestRunLog



def get_campaign_endpoint(
    config: CloudConfig,
) -> str | None:

    explicit_endpoint = os.getenv(
        "VETP_CLOUD_CAMPAIGN_ENDPOINT"
    )

    if explicit_endpoint:
        return explicit_endpoint

    if not config.endpoint:
        return None

    endpoint = config.endpoint.rstrip("/")

    if endpoint.endswith("/api/v1/runs"):
        return (
            endpoint.removesuffix("/api/v1/runs")
            + "/api/v1/campaigns"
        )

    if endpoint.endswith("/api/v1/campaigns"):
        return endpoint

    return None



def publish_campaign_http(
    summary: CloudCampaignSummary,
    config: CloudConfig,
) -> CloudPublishResult:

    
    request_body = cloud_campaign_to_json(
        summary
    ).encode("utf-8")

    endpoint = get_campaign_endpoint(config)

    if not endpoint:
        return CloudPublishResult(
            run_id=summary.campaign_id,
            success=False,
            destination="",
            message="No campaign API endpoint configured.",
            status_code=None,
        )

    request = Request(
        url=endpoint,
        data=request_body,
        method="POST",
    )

    request.add_header(
        "Content-Type",
        "application/json",
    )

    try:

        with urlopen(
            request,
            timeout=config.timeout_seconds,
        ) as response:

            status_code = response.status

            response_text = (
                response.read().decode("utf-8")
            )

            try:
                response_payload = json.loads(
                    response_text
                )
            except json.JSONDecodeError:
                response_payload = {}

            if not isinstance(response_payload, dict):
                response_payload = {}

            accepted = (
                status_code == 201
                and response_payload.get("accepted") is True
                and response_payload.get("campaign_id")
                == summary.campaign_id
            )

            return CloudPublishResult(
                run_id=summary.campaign_id,
                success=accepted,
                destination=endpoint,
                message=response_payload.get(
                    "message",
                    "API request completed.",
                ),
                status_code=status_code,
            )

    except HTTPError as exc:

        return CloudPublishResult(
            run_id=summary.campaign_id,
            success=False,
            destination=endpoint,
            message=f"HTTP error: {exc.code}",
            status_code=exc.code,
        )

    except URLError as exc:

        return CloudPublishResult(
            run_id=summary.campaign_id,
            success=False,
            destination=endpoint,
            message=f"Connection failed: {exc.reason}",
            status_code=None,
        )


def prepare_and_publish_campaign(
    test_logs: tuple[TestRunLog, ...],
    device_id: str,
    config: CloudConfig,
    campaign_id: str | None = None,
) -> tuple[Path, CloudPublishResult]:

    
    summary = build_cloud_campaign_summary(
        test_logs=test_logs,
        device_id=device_id,
        campaign_id=campaign_id,
    )

    
    outbox_path = save_campaign_to_outbox(
        summary
    )

    
    if config.mode == "api":

        result = publish_campaign_http(
            summary,
            config,
        )

    elif config.mode == "local":

        result = CloudPublishResult(
            run_id=summary.campaign_id,
            success=True,
            destination=str(outbox_path),
            message="Campaign prepared in local outbox.",
            status_code=None,
        )

    else:

        result = CloudPublishResult(
            run_id=summary.campaign_id,
            success=False,
            destination="",
            message=(
                f"Unsupported cloud mode: {config.mode}"
            ),
            status_code=None,
        )

    return outbox_path, result