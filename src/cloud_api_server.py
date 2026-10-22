from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
import json

from pathlib import Path
import re


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

        if self.path != "/api/v1/runs":
            self.send_error(
                404,
                "Endpoint not found.",
            )
            return

        content_length = int(
            self.headers.get(
                "Content-Length",
                "0",
            )
        )

        request_body = (
            self.rfile.read(
                content_length
            )
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
            self.send_error(
                400,
                "Invalid JSON payload.",
            )
            return

        validation_errors = (
            validate_received_run(
                payload
            )
        )

        if validation_errors:
            self.send_json_response(
                status_code=400,
                payload={
                    "accepted": False,
                    "errors":
                        validation_errors,
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