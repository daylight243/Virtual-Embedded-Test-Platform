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



def main() -> None:
    print("========================================")
    print(" Virtual Embedded Test Platform")
    print(" Python -> FPGA Integration")
    print("========================================")
    print("")

    print("Creating FPGA input vectors...")
    vectors = build_demo_vectors()
    write_vectors(
        vectors=vectors,
        output_path = FPGA_INPUT_FILE,
    )
    print("FPGA input vectors created.")
    print("")

    try:

        print("Compiling virtual FPGA...")

        compile_fpga()

        print("FPGA compilation successful.")
        print("")

        print("Running virtual FPGA...")
        print("")

        output = run_fpga_simulation()

        print(output)

        print("Python received FPGA simulation result.")
        print("")

        if fpga_tests_passed(output):
            print("INTEGRATION RESULT: PASS")
        else:
            print("INTEGRATION RESULT: FAIL")

    except RuntimeError as error:
        print("")
        print("INTEGRATION ERROR")
        print("-----------------")
        print(error)
        print("")
        print("INTEGRATION RESULT: FAIL")


if __name__ == "__main__":
    main()


        
