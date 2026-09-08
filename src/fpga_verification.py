from dataclasses import dataclass
from fpga_results import (
    FPGA_result,
    STATE_NAMES,
    FAULT_NAMES,
)
@dataclass(frozen=True)
class FPGAExpectation:
    timestamp: int
    state_code: int
    fault_code: int
    alarm: int
    shutdown: int

    def validate_bit (
        self,
        name: str,
        value: int,
    ) -> None:
        if value not in (0, 1):
            raise ValueError(
                f"{name} must be 0 or 1, got {value}"
                )

    def validate(self) -> None:
        if self.timestamp < 0:
            raise ValueError(
                f"timestamp must be non-negative, "
                f"got {self.timestamp}"
            )

        if self.state_code not in STATE_NAMES:
            raise ValueError(
                f"Unknown expected state code: "
                f"{self.state_code}"
            )

        if self.fault_code not in FAULT_NAMES:
            raise ValueError(
                f"Unknown expected fault code: "
                f"{self.fault_code}"
            )

        self.validate_bit(
            "expected alarm",
            self.alarm,
            )

        self.validate_bit(
            "expected shutdown",
            self.shutdown,
            )

@dataclass(frozen = True)
class VerificationResult:
    timestamp: int
    passed: bool
    expected: FPGAExpectation
    actual: FPGA_result
    mismatches: tuple[str,...]

def compare_result(
    expected: FPGAExpectation,
    actual: FPGA_result,
) -> VerificationResult:

    expected.validate()
    actual.validate()

    mismatches = []

    if actual.timestamp != expected.timestamp:
            mismatches.append(
                "timestamp: "
                f"expected {expected.timestamp}, "
                f"got {actual.timestamp}"
            )

    if actual.state_code != expected.state_code:
        mismatches.append(
            "state: "
            f"expected "
            f"{STATE_NAMES[expected.state_code]}, "
            f"got "
            f"{STATE_NAMES[actual.state_code]}"
        )

    if actual.fault_code != expected.fault_code:
        mismatches.append(
            "fault: "
            f"expected "
            f"{FAULT_NAMES[expected.fault_code]}, "
            f"got "
            f"{FAULT_NAMES[actual.fault_code]}"
        )

    if actual.alarm != expected.alarm:
        mismatches.append(
            "alarm: "
            f"expected {expected.alarm}, "
            f"got {actual.alarm}"
        )

    if actual.shutdown != expected.shutdown:
        mismatches.append(
            "shutdown: "
            f"expected {expected.shutdown}, "
            f"got {actual.shutdown}"
        )

    return VerificationResult(
        timestamp=expected.timestamp,
        passed=len(mismatches) == 0,
        expected=expected,
        actual=actual,
        mismatches=tuple(mismatches),
    )

def build_demo_expectations() -> list[FPGAExpectation]:
    return [
        FPGAExpectation(
            timestamp=0,
            state_code=0,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=1,
            state_code=1,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=2,
            state_code=2,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=3,
            state_code=2,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=4,
            state_code=2,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=5,
            state_code=2,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGAExpectation(
            timestamp=6,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=1,
        ),
        FPGAExpectation(
            timestamp=7,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=1,
        ),
    ]
def verify_results(
        expectations: list[FPGAExpectation],
        actual_result: list[FPGA_result],
    ) -> list[VerificationResult]:

    if len(expectations) != len(actual_result):
        raise ValueError(
            "Expected and actual result counts "
            "do not match."
        )

    verification_results = []

    for expected, actual in zip(
        expectations,
        actual_result
    ):
        verification_results.append(
            compare_result(
                expected=expected,
                actual = actual,
            )
        )


    return verification_results

def verification_passed(
        results: list[VerificationResult],
) -> bool:
    return all(
        result.passed
        for result in results
    )

def print_verification_report(
    results: list[VerificationResult],
) -> None:

    print("========================================")
    print(" FPGA EXPECTED vs ACTUAL VERIFICATION")
    print("========================================")
    print("")

    for result in results:

        status = (
            "PASS"
            if result.passed
            else "FAIL"
        )

        print(
            f"t={result.timestamp} | "
            f"{status} | "
            f"state={result.actual.state_name} | "
            f"fault={result.actual.fault_name} | "
            f"alarm={result.actual.alarm} | "
            f"shutdown={result.actual.shutdown}"
        )

        if not result.passed:

            for mismatch in result.mismatches:

                print(
                    f"    - {mismatch}"
                )

    print("")

    if verification_passed(results):
        print("FPGA BEHAVIOUR RESULT: PASS")
    else:
        print("FPGA BEHAVIOUR RESULT: FAIL")

    print("========================================")

if __name__ == "__main__":
    from pathlib import Path
    from fpga_results import (read_FPGA_results,)

    project_root = (Path(__file__).resolve().parents[1])

    output_path = (
        project_root/"build"/"fpga_outputs.csv"
    )

    actual_results = read_FPGA_results(
        output_path
    )

    expectations = (
        build_demo_expectations()
    )

    results = verify_results(
        expectations=expectations,
        actual_result=actual_results,
    )

    print_verification_report(
        results
    )


