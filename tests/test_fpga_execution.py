from fpga_runner import (
    run_python_integration,
)

def test_hdl_execution_completes():

    integration_output = (
        run_python_integration()
    )

    assert (
        "PYTHON -> FPGA RESULT: PASS"
        in integration_output
    )

from fpga_runner import (
    run_python_integration,
    run_engineering_test,
)

from fpga_test_cases import (
    build_engineering_test_cases,
)


def test_hdl_execution_completes():

    integration_output = (
        run_python_integration()
    )

    assert (
        "PYTHON -> FPGA RESULT: PASS"
        in integration_output
    )


def test_known_startup_scenario_end_to_end():


    test_cases = (
        build_engineering_test_cases()
    )


    startup_test = test_cases[0]


    assert (
        startup_test.test_id
        == "TC-001"
    )

    test_log = run_engineering_test(
        startup_test
    )

    assert (
        test_log.test_id
        == startup_test.test_id
    )

    assert (
        test_log.passed
        is True
    )

    assert (
        test_log.errors
        == ()
    )