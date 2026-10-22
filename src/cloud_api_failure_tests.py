import json

from urllib.request import (
    Request,
    urlopen,
)

from urllib.error import (
    HTTPError,
    URLError,
)


API_ENDPOINT = (
    "http://127.0.0.1:8000/api/v1/runs"
)


def build_demo_payload(
    passed: bool = True,
) -> dict:

    return {
        "schema_version": "1.0",
        "run_id": "API-DEMO-001",
        "device_id": "DEMO-DEVICE",
        "test_id": "TC-DEMO",
        "test_name": "Controlled API Test",
        "started_at_utc": (
            "2026-10-20T00:00:00Z"
        ),
        "passed": passed,
    }



def send_test_request(
    payload: dict,
    endpoint: str = API_ENDPOINT,
) -> None:

    request_body = json.dumps(
        payload
    ).encode("utf-8")

    request = Request(
        url=endpoint,
        data=request_body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:

        with urlopen(
            request,
            timeout=5,
        ) as response:

            response_text = (
                response.read().decode("utf-8")
            )

            print(
                f"HTTP status: {response.status}"
            )

            print(
                f"Response: {response_text}"
            )

    except HTTPError as error:

        print(
            f"HTTP error: {error.code}"
        )

        print(
            error.read().decode("utf-8")
        )

    except URLError as error:

        print(
            f"Connection failed: {error.reason}"
        )



def test_missing_run_id() -> None:

    payload = build_demo_payload()

    del payload["run_id"]

    send_test_request(
        payload
    )



def test_failed_engineering_result() -> None:

    payload = build_demo_payload(
        passed=False
    )

    send_test_request(
        payload
    )


def test_wrong_endpoint() -> None:

    payload = build_demo_payload()

    send_test_request(
        payload,
        endpoint=(
            "http://127.0.0.1:8000/api/v1/wrong"
        ),
    )



if __name__ == "__main__":

    print("VETP API Failure Experiments")
    print("1. Missing run_id")
    print("2. Valid FAIL result")
    print("3. Wrong endpoint path")

    selection = input(
        "Select experiment (1–3): "
    ).strip()

    if selection == "1":
        test_missing_run_id()

    elif selection == "2":
        test_failed_engineering_result()

    elif selection == "3":
        test_wrong_endpoint()

    else:
        print("Invalid selection.")