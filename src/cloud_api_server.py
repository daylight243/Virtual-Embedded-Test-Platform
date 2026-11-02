from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
import json

from pathlib import Path
import re

import os
import tempfile
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CAMPAIGN_INBOX_DIR = (
    PROJECT_ROOT
    / "build"
    / "cloud_inbox"
    / "campaigns"
)

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CLOUD_INBOX_DIR = (
    PROJECT_ROOT
    / "build"
    / "cloud_inbox"
)

REQUIRED_RUN_FIELDS = {
    "schema_version",
    "run_id",
    "device_id",
    "test_id",
    "test_name",
    "started_at_utc",
    "passed",
}

def validate_received_run(
    payload: object,
) -> list[str]:

    errors: list[str] = []

    if not isinstance(
        payload,
        dict,
    ):
        return [
            "Payload must be "
            "a JSON object."
        ]

    missing_fields = (
        REQUIRED_RUN_FIELDS
        - payload.keys()
    )

    for field_name in sorted(
        missing_fields
    ):
        errors.append(
            f"Missing field: "
            f"{field_name}"
        )

    if (
        "passed" in payload
        and not isinstance(
            payload["passed"],
            bool,
        )
    ):
        errors.append(
            "passed must be "
            "a boolean."
        )

    return errors

def safe_filename_part(
    value: str,
) -> str:

    return re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        value,
    )

def save_received_run(
    payload: dict,
) -> Path:

    CLOUD_INBOX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_run_id = (
        safe_filename_part(
            str(payload["run_id"])
        )
    )

    output_path = (
        CLOUD_INBOX_DIR
        / f"run_{safe_run_id}.json"
    )

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path

class VETPRequestHandler(
    BaseHTTPRequestHandler
):
     def do_POST(self) -> None:


        if self.path not in (
            "/api/v1/runs",
            "/api/v1/campaigns",
        ):

            self.send_json_response(
                status_code=404,
                payload={
                    "accepted": False,
                    "errors": [
                        "Unknown endpoint."
                    ],
                },
            )
            return

        

        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

        except ValueError:

            self.send_json_response(
                status_code=400,
                payload={
                    "accepted": False,
                    "errors": [
                        "Invalid Content-Length."
                    ],
                },
            )
            return

        request_body = self.rfile.read(
            content_length
        )

        
        try:

            payload = json.loads(
                request_body.decode(
                    "utf-8"
                )
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):

            self.send_json_response(
                status_code=400,
                payload={
                    "accepted": False,
                    "errors": [
                        "Invalid JSON payload."
                    ],
                },
            )
            return

        

        if self.path == "/api/v1/runs":

            errors = validate_received_run(
                payload
            )

        elif self.path == "/api/v1/campaigns":

            errors = validate_received_campaign(
                payload
            )

       

        if errors:

            self.send_json_response(
                status_code=400,
                payload={
                    "accepted": False,
                    "errors": errors,
                },
            )
            return

        

        if self.path == "/api/v1/campaigns":

            try:
                save_received_campaign(payload)

            except FileExistsError:

                self.send_json_response(
                    status_code=409,
                    payload={
                        "accepted": False,
                        "campaign_id": payload["campaign_id"],
                        "message": "Campaign already exists.",
                    },
                )
                return

            self.send_json_response(
                status_code=201,
                payload={
                    "accepted": True,
                    "campaign_id": payload["campaign_id"],
                    "message": "Campaign accepted.",
                },
            )
            return
        try:
            save_received_campaign(payload)

        except FileExistsError:
            self.send_json_response(
                409,
                {
                    "accepted": False,
                    "campaign_id": payload["campaign_id"],
                    "message": "Campaign already exists.",
                },
            )
            return
  
        

        save_received_run(
            payload
        )

        self.send_json_response(
            status_code=201,
            payload={
                "accepted": True,
                "run_id": payload["run_id"],
                "message": "VETP run accepted.",
            },
        )



     def send_json_response(
        self,
        status_code: int,
        payload: dict,
     ) -> None:

        response_body = json.dumps(
            payload
        ).encode("utf-8")

        self.send_response(
            status_code
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(response_body)),
        )

        self.end_headers()

        self.wfile.write(
            response_body
        )

def validate_received_campaign(
    payload: object,
) -> list[str]:

    if not isinstance(payload, dict):
        return ["Payload must be a JSON object."]

    required = {
        "schema_version",
        "campaign_id",
        "created_at_utc",
        "device_id",
        "total_tests",
        "passed_tests",
        "failed_tests",
        "pass_rate_percent",
        "overall_passed",
        "runs",
    }

    errors = []

    for field in sorted(required - payload.keys()):
        errors.append(
            f"Missing field: {field}"
        )

    if errors:
        return errors

    if payload["schema_version"] != "1.0":
        errors.append("Unsupported schema version.")

    for field in (
        "campaign_id",
        "created_at_utc",
        "device_id",
    ):
        if (
            not isinstance(payload[field], str)
            or not payload[field].strip()
        ):
            errors.append(f"Invalid {field}.")

    runs = payload["runs"]

    if not isinstance(runs, list) or not runs:
        errors.append("runs must be a nonempty list.")
        return errors

    seen_ids = set()
    passed = 0

    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            errors.append(
                f"Run {index} must be an object."
            )
            continue

        run_id = run.get("run_id")
        test_id = run.get("test_id")
        result = run.get("passed")

        if not isinstance(run_id, str) or not run_id:
            errors.append(f"Invalid run_id at {index}.")
        elif run_id in seen_ids:
            errors.append("Duplicate run_id.")
        else:
            seen_ids.add(run_id)

        if not isinstance(test_id, str) or not test_id:
            errors.append(f"Invalid test_id at {index}.")

        if type(result) is not bool:
            errors.append(f"Invalid passed at {index}.")
        elif result:
            passed += 1

    total = len(runs)
    failed = total - passed

    expected = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
    }

    for field, value in expected.items():
        if (
            type(payload[field]) is not int
            or payload[field] != value
        ):
            errors.append(f"Incorrect {field}.")

    if (
        type(payload["overall_passed"]) is not bool
        or payload["overall_passed"] != (failed == 0)
    ):
        errors.append("Incorrect overall_passed.")

    rate = round(passed / total * 100, 2)

    supplied_rate = payload["pass_rate_percent"]

    if (
        type(supplied_rate) not in (int, float)
        or not 0 <= supplied_rate <= 100
        or abs(supplied_rate - rate) > 0.001
    ):
        errors.append("Incorrect pass_rate_percent.")

    return errors

def save_received_campaign(
    payload: dict,
) -> Path:

    CAMPAIGN_INBOX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_id = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        payload["campaign_id"],
    )

    destination = (
        CAMPAIGN_INBOX_DIR
        / f"campaign_{safe_id}.json"
    )

    content = json.dumps(
        payload,
        indent=2,
    ).encode("utf-8")

    # The destination is created exclusively.
    # Duplicate IDs must not silently overwrite evidence.
    with destination.open("xb") as output:
        output.write(content)

    return destination

def run_api_server() -> None:

    host = "127.0.0.1"
    port = 8000

    server = ThreadingHTTPServer(
        (host, port),
        VETPRequestHandler,
    )

    print(
        f"VETP API listening at "
        f"http://{host}:{port}",
        flush=True,
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping VETP API server.")

    finally:
        server.server_close()


if __name__ == "__main__":
    run_api_server()
