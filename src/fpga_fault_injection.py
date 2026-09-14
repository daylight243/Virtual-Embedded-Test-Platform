from dataclasses import dataclass, replace
from fpga_vectors import FPGATestVector

FAULT_FIELDS = {
    "undervoltage":"uv",
    "overvoltage":"ov",
    "overcurrent":"oc",
    "overtemperature":"ot"
}

@dataclass(frozen=True)
class FaultInjection:
    fault: str
    start_timestamp: int
    duration: int

    def validate(self) -> None:

        if self.fault not in FAULT_FIELDS:
            raise ValueError(
                f"Unsupported fault: {self.fault}"
            )

        if self.start_timestamp < 0:
            raise ValueError(
                "start_timestamp must be "
                "non-negative."
            )

        if self.duration <= 0:
            raise ValueError(
                "duration must be greater "
                "than zero."
            )

    @property
    def end_timestamp_exclusive(self) -> int:
            return self.start_timestamp + self.duration

    def active_at(self, timestamp: int) -> bool:
            return self.start_timestamp <= timestamp < self.end_timestamp_exclusive

def apply_injection_to_vector(vectors: FPGATestVector, injection: FaultInjection) -> FPGATestVector:
    injection.validate()
    if not injection.active_at(vectors.timestamp):
        return vectors

    field_name = FAULT_FIELDS[injection.fault]
    return replace(vectors, **{field_name: 1})

def validate_injections_against_vectors(vectors: list[FPGATestVector], injections: list[FaultInjection]) -> None:
    if not vectors:
        raise ValueError(
            "Cannot inject faults into "
            "an empty vector sequence."
        )

    available_timestamps = {vector.timestamp for vector in vectors}
    for injection in injections:
        injection.validate()
       
        injection_timestamps = set(
            range(
                injection.start_timestamp,
                injection.end_timestamp_exclusive,
            )
        )

        missing_timestamps = (
            injection_timestamps
            - available_timestamps
        )

        if missing_timestamps:

            raise ValueError(
                "Fault injection extends outside "
                "the available scenario timestamps: "
                f"{sorted(missing_timestamps)}"
            )

def apply_fault_injections(vectors: list[FPGATestVector], injections: list[FaultInjection]) -> list[FPGATestVector]:

    validate_injections_against_vectors(vectors = vectors, injections = injections)

    result = []
    for vector in vectors:
         modified_vector = vector
         for injection in injections:
             modified_vector = apply_injection_to_vector(modified_vector, injection)
         result.append(modified_vector)

    return result

def print_faulted_vectors(
    vectors: list[FPGATestVector],
) -> None:

    print(
        "timestamp | UV OV OC OT"
    )

    for vector in vectors:

        print(
            f"{vector.timestamp:>9} | "
            f"{vector.uv}  "
            f"{vector.ov}  "
            f"{vector.oc}  "
            f"{vector.ot}"
        )
