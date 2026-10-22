import json
from urllib.request import (
    Request,
    urlopen,
)


payload = {
    "schema_version": "1.0",
    "run_id": "SMOKE-TEST-001",
    "device_id": "DEMO-DEVICE",
    "test_id": "TC-DEMO",
    "test_name": "API Smoke Test",
    "started_at_utc":
        "2026-01-01T00:00:00Z",
    "passed": True,
}


body = json.dumps(
    payload
).encode("utf-8")


request = Request(
    url=(
        "http://127.0.0.1:"
        "8000/api/v1/runs"
    ),
    data=body,
    headers={
        "Content-Type":
            "application/json",
    },
    method="POST",
)


with urlopen(
    request,
    timeout=5.0,
) as response:

    response_body = (
        response.read()
        .decode("utf-8")
    )

    print(response.status)
    print(response_body)