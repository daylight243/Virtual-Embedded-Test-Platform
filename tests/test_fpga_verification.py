from fpga_results import FPGA_result
from fpga_verification import (
    FPGAExpectation,
    verify_results,
    verification_passed,
)
def test_matching_expected_and_actual_pass():
    expectations = [
        FPGAExpectation(
            timestamp=6,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=1,
        )
    ]
    actual = [
        FPGA_result(
            timestamp=6,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=1,
        )
    ]
    results = verify_results(
        expectations=expectations,
        actual_result=actual,
    )
    assert results[0].passed is True
    assert verification_passed(results) is True

def test_shutdown_mismatch_fails():
    expectations = [
        FPGAExpectation(
            timestamp=6,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=1,
        )
    ]
    actual = [
        FPGA_result(
            timestamp=6,
            state_code=3,
            fault_code=3,
            alarm=1,
            shutdown=0,
        )
    ]
    results = verify_results(
        expectations=expectations,
        actual_result=actual,
    )
    assert results[0].passed is False
    assert verification_passed(results) is False
    assert any(
        "shutdown" in mismatch.lower()
        for mismatch
        in results[0].mismatches
    )