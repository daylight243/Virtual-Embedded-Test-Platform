from pathlib import Path
import subprocess
from fpga_vectors import (build_demo_vectors, write_vectors)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HDL_DIR = PROJECT_ROOT / "hdl"
BUILD_DIR = PROJECT_ROOT / "build"

SIMULATION_OUTPUT = BUILD_DIR / "protection_controller_sim"

FPGA_INPUT_FILE = BUILD_DIR / "fpga_inputs.csv"

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


    except RuntimeError as error:
        print("")
        print("INTEGRATION ERROR")
        print("-----------------")
        print(error)
        print("")
        print("INTEGRATION RESULT: FAIL")


if __name__ == "__main__":
    main()


        
