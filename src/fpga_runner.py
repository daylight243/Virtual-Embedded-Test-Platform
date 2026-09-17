from pathlib import Path
import subprocess
from fpga_vectors import (build_demo_vectors, write_vectors)
from fpga_results import (read_FPGA_results, validate_input_output_alignment)
from fpga_verification import (
    build_demo_expectations,
    verify_results,
    verification_passed,
    print_verification_report,
)
from fpga_test_cases import (
    EngineeringTestCase,
    build_engineering_test_cases,
)
from test_logging import (
    TestRunLog,
    CampaignSummary,
    build_test_run_log,
    save_test_run_log,
    build_error_test_run_log,
    build_campaign_summary,
    save_campaign_summary,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HDL_DIR = PROJECT_ROOT / "hdl"
BUILD_DIR = PROJECT_ROOT / "build"

SIMULATION_OUTPUT = BUILD_DIR / "protection_controller_sim"

FPGA_INPUT_FILE = BUILD_DIR / "fpga_inputs.csv"
FPGA_OUTPUT_FILE = BUILD_DIR / "fpga_outputs.csv"


VERILOG_SOURCES = [
    HDL_DIR / "fault_priority.v",
    HDL_DIR / "fault_persistence.v",
    HDL_DIR / "fault_latch.v",
    HDL_DIR / "protection_state_register.v",
    HDL_DIR / "protection_next_state.v",
    HDL_DIR / "protection_outputs.v",
    HDL_DIR / "protection_fsm.v",
    HDL_DIR / "tb_protection_controller.v",
]

CONTROLLER_SOURCES = [
    HDL_DIR / "fault_priority.v",
    HDL_DIR / "fault_persistence.v",
    HDL_DIR / "fault_latch.v",
    HDL_DIR / "protection_state_register.v",
    HDL_DIR / "protection_next_state.v",
    HDL_DIR / "protection_outputs.v",
    HDL_DIR / "protection_fsm.v",
]

HDL_VERIFICATION_TESTBENCH = (
    HDL_DIR / "tb_protection_controller.v"
)
PYTHON_INTEGRATION_TESTBENCH = (
    HDL_DIR / "tb_python_integration.v"
)

HDL_VERIFICATION_OUTPUT = (
    BUILD_DIR / "protection_controller_sim"
)

PYTHON_INTEGRATION_OUTPUT = (
    BUILD_DIR / "python_integration_sim"
)

TEST_LOG_DIR = (
    BUILD_DIR / "test_logs"
)

CAMPAIGN_LOG_DIR = (
    BUILD_DIR / "campaign_logs"
)

def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

def compile_fpga() -> None:

    BUILD_DIR.mkdir(exist_ok = True)

    command = ["iverilog",
        "-I",
        str(HDL_DIR),
        "-o",
        str(SIMULATION_OUTPUT),
    ]

    command.extend(str(source) for source in VERILOG_SOURCES)

    result = run_command(command)

    if result.returncode != 0:
        raise RuntimeError(
            "Failed compilation failed.\n\n"
            f"{result.stderr}"
        )

def prepare_test_case(
    test_case: EngineeringTestCase,
) -> None:

    write_vectors(
        list(test_case.vectors),
        FPGA_INPUT_FILE,
    )

def run_fpga_simulation() -> str:
    command = [
    "vvp",
    str(SIMULATION_OUTPUT),
    ]

    result = run_command(command)

    if result.returncode != 0:
        raise RuntimeError(
        "FPGA simulation failed.\n\n"
        f"{result.stderr}"
    )

    return result.stdout

def fpga_tests_passed(output: str) -> bool:
    return "MISSION 3 HDL RESULT: PASS" in output

def compile_simulation(
    testbench: Path,
    output_path: Path,
) -> None:
    BUILD_DIR.mkdir(exist_ok=True)

    command = [
        "iverilog",
        "-I",
        str(HDL_DIR),
        "-o",
        str(output_path),
    ]

    command.extend(
        str(source)
        for source in CONTROLLER_SOURCES
    )

    command.append(str(testbench))

    result = run_command(command)

    if result.returncode != 0:
        raise RuntimeError(
            "HDL compilation failed.\n\n"
            f"{result.stderr}"
        )

def run_simulation(
    simulation_path: Path,
) -> str:
    result = run_command(
        [
            "vvp",
            str(simulation_path),
        ]
    )

    if result.returncode != 0:
        raise RuntimeError(
            "HDL simulation failed.\n\n"
            f"{result.stderr}"
        )

    return result.stdout

def run_hdl_verification() -> str:
    compile_simulation(
        testbench=HDL_VERIFICATION_TESTBENCH,
        output_path=HDL_VERIFICATION_OUTPUT,
    )

    return run_simulation(
        HDL_VERIFICATION_OUTPUT
    )

def run_python_integration() -> str:
    compile_simulation(
        testbench=PYTHON_INTEGRATION_TESTBENCH,
        output_path=PYTHON_INTEGRATION_OUTPUT,
    )

    return run_simulation(
        PYTHON_INTEGRATION_OUTPUT
    )

def run_engineering_test(
test_case: EngineeringTestCase,
) -> TestRunLog:

    print("")
    print("========================================")
    print(
        f"{test_case.test_id} | "
        f"{test_case.name}"
    )
    print("========================================")
    print("")

   

    try:
        test_case.validate()
        # -------------------------------------
        # 1. Write this test's FPGA vectors
        # -------------------------------------

        write_vectors(
            vectors=list(test_case.vectors),
            output_path=FPGA_INPUT_FILE,
        )

        # -------------------------------------
        # 2. Run the FPGA simulation
        # -------------------------------------

        integration_output = (
            run_python_integration()
        )

        if (
            "PYTHON -> FPGA RESULT: PASS"
            not in integration_output
        ):
            raise RuntimeError(
                f"{test_case.test_id}: "
                "Python-to-FPGA integration failed."
            )

        # -------------------------------------
        # 3. Read the FPGA output
        # -------------------------------------

        actual_results = (
            read_FPGA_results(
                FPGA_OUTPUT_FILE
            )
        )

        # -------------------------------------
        # 4. Check input/output alignment
        # -------------------------------------

        input_timestamps = [
            vector.timestamp
            for vector in test_case.vectors
        ]

        validate_input_output_alignment(
            input_timestamps=input_timestamps,
            results=actual_results,
        )

        # -------------------------------------
        # 5. Verify actual vs expected results
        # -------------------------------------

        verification_results = (
            verify_results(
                expectations=list(
                    test_case.expectations
                ),
                actual_result=actual_results,
            )
        )

        passed = verification_passed(
            verification_results
        )

        print_verification_report(
            verification_results
        )

        # -------------------------------------
        # 6. Build the test log
        # -------------------------------------

        test_log = build_test_run_log(
            test_case=test_case,
            actual_results=actual_results,
            verification_results=(
                verification_results
            ),
            passed=passed,
        )

        # -------------------------------------
        # 7. Save the test log
        # -------------------------------------

        log_path = save_test_run_log(
            test_log=test_log,
            output_directory=TEST_LOG_DIR,
        )

        print("")
        print(
            f"Test log saved: {log_path}"
        )

        # -------------------------------------
        # 8. Return the log object
        # -------------------------------------

        return test_log

    except Exception as error:

        error_log = (
            build_error_test_run_log(
                test_case=test_case,
                error_message=str(error),
            )
        )

        log_path = save_test_run_log(
            test_log=error_log,
            output_directory=TEST_LOG_DIR,
        )

        print("")
        print(
            f"Failure log saved: "
            f"{log_path}"
        )

        return error_log

def run_test_campaign(
    test_cases: list[EngineeringTestCase],
) -> CampaignSummary:

    print("")
    print("========================================")
    print(" ENGINEERING TEST CAMPAIGN")
    print("========================================")
    print("")

    test_logs = []

    for test_case in test_cases:

        test_log = run_engineering_test(
            test_case
        )

        test_logs.append(
            test_log
        )

    summary = build_campaign_summary(
        test_logs
    )

    summary_path = save_campaign_summary(
        summary=summary,
        output_directory=CAMPAIGN_LOG_DIR,
    )

    print("")
    print("========================================")
    print(" CAMPAIGN SUMMARY")
    print("========================================")
    print("")

    print(
        f"Total tests:  "
        f"{summary.total_tests}"
    )

    print(
        f"Passed tests: "
        f"{summary.passed_tests}"
    )

    print(
        f"Failed tests: "
        f"{summary.failed_tests}"
    )

    print("")

    print(
        f"Overall result: "
        f"{'PASS' if summary.overall_passed else 'FAIL'}"
    )

    print("")

    print(
        f"Campaign summary saved: "
        f"{summary_path}"
    )

    print("========================================")

    return summary




def main() -> None:
    print("========================================")
    print(" Virtual Embedded Test Platform")
    print(" Python -> FPGA Integration")
    print("========================================")
    print("")

    try:
        print("Creating FPGA input vectors...")

        vectors = build_demo_vectors()

        write_vectors(
            vectors=vectors,
            output_path=FPGA_INPUT_FILE,
        )

        print("FPGA input vectors created.")
        print("")


        print("Running independent HDL verification...")

        hdl_output = run_hdl_verification()

        if (
            "MISSION 3 HDL RESULT: PASS"
            not in hdl_output
        ):
            raise RuntimeError(
                "Independent FPGA verification failed."
            )

        print("Independent HDL verification: PASS")
        print("")


        print("Running Python-driven FPGA simulation...")
        print("")

        integration_output = run_python_integration()

        print(integration_output)


        if (
            "PYTHON -> FPGA RESULT: PASS"
            not in integration_output
        ):
            raise RuntimeError(
                "Python-to-FPGA integration failed."
            )


        print("INTEGRATION RESULT: PASS")
        print("Reading FPGA output file...")

        results = read_FPGA_results(
            FPGA_OUTPUT_FILE
        )

        print(
            f"FPGA results read: {len(results)}"
        )
        print("")

        input_timestamps = [
            vector.timestamp
            for vector in vectors
        ]

        validate_input_output_alignment(
            input_timestamps=input_timestamps,
            results=results,
        )

        expectations = (
        build_demo_expectations()
        )

        verification_results = verify_results(
            expectations=expectations,
            actual_result=results,
        )

        print("FPGA result summary:")
        print("")

        for result in results:

            print(
                f"t={result.timestamp} | "
                f"{result.state_name:<8} | "
                f"{result.fault_name:<15} | "
                f"alarm={result.alarm} | "
                f"shutdown={result.shutdown}"
            )
        print_verification_report(
        verification_results
        )
        if not verification_passed(
            verification_results
        ):
            raise RuntimeError(
                "FPGA behaviour did not match "
                "the expected results."
            )

    except RuntimeError as error:
        print("")
        print("INTEGRATION ERROR")
        print("-----------------")
        print(error)
        print("")
        print("INTEGRATION RESULT: FAIL")

    print("")
    print("Running engineering test campaign...")
    print("")

    test_cases = build_engineering_test_cases()

    campaign_summary = run_test_campaign(
        test_cases
    )

    print("")

    if campaign_summary.overall_passed:
        print(
            "ENGINEERING CAMPAIGN RESULT: PASS"
        )
    else:
        print(
            "ENGINEERING CAMPAIGN RESULT: FAIL"
        )


if __name__ == "__main__":
    main()


        
