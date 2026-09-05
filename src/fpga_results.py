from dataclasses import dataclass
from pathlib import Path

CSV_HEADER = (
    "timestamp,state_code,fault_code,"
    "alarm,shutdown"
)

STATE_NAMES = {
    0: "IDLE",
    1: "STARTUP",
    2: "RUNNING",
    3: "FAULT",
    4: "RECOVERY",
}

FAULT_NAMES = {
    0: "NONE",
    1: "UNDERVOLTAGE",
    2: "OVERVOLTAGE",
    3: "OVERCURRENT",
    4: "OVERTEMPERATURE",
}

def validate_bit(
        name: str,
        value: int,
    ) -> None:
        if value not in (0, 1):
            raise ValueError(
                f"{name} must be 0 or 1, got {value}"
            )


@dataclass(frozen = True)
class FPGA_result:
    timestamp:  int
    state_code: int
    fault_code: int
    alarm:      int
    shutdown:   int

    @property 
    def state_name(self) -> str:
        return STATE_NAMES.get(
            self.state_code, "UNKOWN",
        )

    @property
    def fault_name(self) -> str:
        return FAULT_NAMES.get(
            self.fault_code, "UNKOWN",
        )


    def validate(self) -> None: 
        if self.timestamp < 0:
            raise ValueError(
                f"timestamp must be non-negative, "
                f"got {self.timestamp}"
            )
        if self.state_code not in STATE_NAMES:
            raise ValueError(
                f"Unknown FPGA state code: "
                f"{self.state_code}"
            )
        if self.fault_code not in FAULT_NAMES:
            raise ValueError(
                f"Unknown FPGA fault code: "
                f"{self.fault_code}"
            )

        validate_bit("alarm", self.alarm)
        validate_bit("shutdown", self.shutdown)

def result_from_csv_row(
         row:str,
) -> FPGA_result:
    parts = row.strip().split(",")

    if len(parts) != 5:
        raise ValueError(
            f"Expected 5 fields, "
            f"got {len(parts)}: {row}"
        )

    result = FPGA_result(
        timestamp= int(parts[0]),
        state_code = int(parts[1]),
        fault_code=int(parts[2]),
        alarm=int(parts[3]),
        shutdown=int(parts[4]),
    )
    result.validate()
    return result

def validate_result_sequence(
        results: list[FPGA_result]
) -> None:
    previous_timestamp = -1

    for result in results:
        result.validate()

        if result.timestamp <= previous_timestamp:
            raise ValueError(
                "FPGA result timestamps must increase."
            )
        previous_timestamp = result.timestamp

def read_FPGA_results(
        input_path: Path,
) -> list[FPGA_result]:

    lines = input_path.read_text(
        encoding = "utf-8"
    ).splitlines()
    if lines[0].strip() != CSV_HEADER:
        raise ValueError(
            "Unexpected FPGA output header"
        )
    results = []

    for line in lines[1:]:

        if not line.strip():
            continue

        results.append(
            result_from_csv_row(line)
        )
    validate_result_sequence(results)
    return results

def validate_input_output_alignment(
        input_timestamps: list[int],
        results: list[FPGA_result],) -> None:
    result_timestamps = [
        result.timestamp
        for result in results
    ]
    if input_timestamps != result_timestamps:
        raise ValueError(
            "FPGA input/output timestamps "
            "do not match."
        )
 
    


def main() -> None:
    project_root = (
        Path(__file__).resolve().parents[1]
    )

    result_path = (
        project_root/"build"/"fpga_outputs.csv"
    )

    results = read_FPGA_results(result_path)

    print("========================================")
    print(" FPGA Simulation Results")
    print("========================================")
    print("")

    for result in results:
        print(
            f"t={result.timestamp} | "
            f"state={result.state_name} | "
            f"fault={result.fault_name} | "
            f"alarm={result.alarm} | "
            f"shutdown={result.shutdown}"
        )

    print("")
    print(
        f"Results parsed: {len(results)}"
    )


if __name__ == "__main__":
    main()


