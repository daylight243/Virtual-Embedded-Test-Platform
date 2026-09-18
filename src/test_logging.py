from dataclasses import asdict, dataclass 
from datetime import datetime, timezone

import json

from pathlib import Path

from fpga_results import FPGA_result, STATE_NAMES, FAULT_NAMES  

from fpga_test_cases import (
    EngineeringTestCase,
)

from fpga_verification import (
    VerificationResult,
)

@dataclass(frozen=True)
class TestRunLog:
    run_id: str

    test_id: str
    test_name: str
    description: str

    started_at_utc: str

    measurements: tuple[dict, ...]

    hdl_inputs: tuple[dict, ...]
    expected_results: tuple[dict, ...]
    actual_results: tuple[dict, ...]

    verification_results: tuple[dict, ...]

    passed: bool

    errors: tuple[str, ...]

TestRunLog.__test__ = False

def vector_to_dict(vector) -> dict:
    return asdict(vector)

def fpga_result_to_dict(
result: FPGA_result,
) -> dict:

    return {
        "timestamp": result.timestamp,
        "state_code": result.state_code,
        "state_name": result.state_name,
        "fault_code": result.fault_code,
        "fault_name": result.fault_name,
        "alarm": result.alarm,
        "shutdown": result.shutdown,
    }
def expectation_to_dict(
expectation,
) -> dict:

    return {
        "timestamp": expectation.timestamp,
        "state_code": expectation.state_code,
        "state_name": STATE_NAMES[expectation.state_code],
        "fault_code": expectation.fault_code,
        "fault_name": FAULT_NAMES[expectation.fault_code],
        "alarm": expectation.alarm,
        "shutdown": expectation.shutdown,
    }

def verification_result_to_dict(
result: VerificationResult,
) -> dict:

    return {
        "timestamp": result.timestamp,
        "passed": result.passed,
        "expected": expectation_to_dict(
            result.expected
        ),
        "actual": fpga_result_to_dict(
            result.actual
        ),
        "mismatches": list(
            result.mismatches
        ),
    }
    
def current_utc_timestamp() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()

def create_run_id(
    test_id: str,
) -> str:

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    return (
        f"{test_id}_{timestamp}"
    )

def build_test_run_log(
    test_case: EngineeringTestCase,
    actual_results: list[FPGA_result],
    verification_results: list[
        VerificationResult
    ],
    passed: bool,
    errors: list[str] | None = None,
    measurements: list[dict] | None = None,
) -> TestRunLog:

    if errors is None:
        errors = []

    if measurements is None:
        measurements = []

    return TestRunLog(
        run_id=create_run_id(
            test_case.test_id
        ),

        test_id=test_case.test_id,
        test_name=test_case.name,
        description=test_case.description,

        started_at_utc=(
            current_utc_timestamp()
        ),

        measurements=tuple(
            measurements
        ),

        hdl_inputs=tuple(
            asdict(vector)
            for vector
            in test_case.vectors
        ),

        expected_results=tuple(
            expectation_to_dict(
                expectation
            )
            for expectation
            in test_case.expectations
        ),

        actual_results=tuple(
            fpga_result_to_dict(
                result
            )
            for result
            in actual_results
        ),

        verification_results=tuple(
            verification_result_to_dict(
                result
            )
            for result
            in verification_results
        ),

        passed=passed,

        errors=tuple(errors),
    )

def save_test_run_log(
    test_log: TestRunLog,
    output_directory: Path,
) -> Path:

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"{test_log.run_id}.json"
    )

    output_path.write_text(
        json.dumps(
            asdict(test_log),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path

def build_error_test_run_log(
    test_case: EngineeringTestCase,
    error_message: str,
    measurements: list[dict] | None = None,
) -> TestRunLog:

    if measurements is None:
        measurements = []

    return TestRunLog(
        run_id=create_run_id(
            test_case.test_id
        ),

        test_id=test_case.test_id,
        test_name=test_case.name,
        description=test_case.description,

        started_at_utc=(
            current_utc_timestamp()
        ),

        measurements=tuple(
            measurements
        ),

        hdl_inputs=tuple(
            asdict(vector)
            for vector
            in test_case.vectors
        ),

        expected_results=tuple(
            expectation_to_dict(
                expectation
            )
            for expectation
            in test_case.expectations
        ),

        actual_results=(),

        verification_results=(),

        passed=False,

        errors=(
            error_message,
        ),
    )

@dataclass(frozen=True)
class CampaignSummary:
    campaign_id: str
    created_at_utc: str

    total_tests: int
    passed_tests: int
    failed_tests: int

    overall_passed: bool

    test_runs: tuple[dict, ...]

def create_campaign_id() -> str:

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    return (
        f"campaign_{timestamp}"
    )

def build_campaign_summary(
    test_logs: list[TestRunLog],
) -> CampaignSummary:

    passed_tests = sum(
        1
        for log in test_logs
        if log.passed
    )

    failed_tests = (
        len(test_logs)
        - passed_tests
    )

    return CampaignSummary(
        campaign_id=create_campaign_id(),

        created_at_utc=(
            current_utc_timestamp()
        ),

        total_tests=len(test_logs),

        passed_tests=passed_tests,

        failed_tests=failed_tests,

        overall_passed=(
            failed_tests == 0
        ),

        test_runs=tuple(
            {
                "run_id": log.run_id,
                "test_id": log.test_id,
                "test_name": log.test_name,
                "passed": log.passed,
                "errors": list(
                    log.errors
                ),
            }
            for log in test_logs
        ),
    )

def save_campaign_summary(
    summary: CampaignSummary,
    output_directory: Path,
) -> Path:

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"{summary.campaign_id}.json"
    )

    output_path.write_text(
        json.dumps(
            asdict(summary),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path



