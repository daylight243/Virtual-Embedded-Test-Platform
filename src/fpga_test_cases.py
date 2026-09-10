from dataclasses import dataclass

from fpga_vectors import FPGATestVector
from fpga_verification import FPGAExpectation

@dataclass(frozen = True)
class EngineeringTestCase:
    test_id: str
    name: str
    description: str
    vectors: tuple[FPGATestVector,...]
    expectations: tuple[FPGAExpectation,...]

    def validate(self) -> None:

        if not self.test_id.strip():
            raise ValueError(
                "test_id cannot be empty"
            )
        if not self.name.strip():
            raise ValueError(
                "Test name cannot be empty"
            )
        if not self.vectors:
            raise ValueError(
                "Test must contain at least one vector"
            )

        if len(self.vectors) != len(self.expectations):
            raise ValueError(
                "Vectors and expectation counts must match"
            )

        vector_timestamps = [
            vector.timestamp
            for vector in self.vectors
        ]

        expectation_timestamps = [
            expectation.timestamp
            for expectation in self.expectations
        ]

        if vector_timestamps != expectation_timestamps:
                raise ValueError(
                     "Vector and expectation timestamps must match"
                )

        for vector in self.vectors:
             vector.validate()

        for expectation in self.expectations:
             expectation.validate()

def healthy_startup_vectors() -> list[FPGATestVector]:

    return [
        FPGATestVector(
            timestamp=0,
            reset=1,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
        FPGATestVector(
            timestamp=1,
            reset=0,
            start=1,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
        FPGATestVector(
            timestamp=2,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
    ]

def healthy_startup_expectations() -> list[FPGAExpectation]:

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
    ]

def build_normal_startup_test() -> EngineeringTestCase:

    test_case = EngineeringTestCase(
        test_id="TC-001",
        name="Normal Startup",
        description=(
            "Verify reset to IDLE, "
            "START transition to STARTUP, "
            "and automatic transition to RUNNING."
        ),
        vectors=tuple(
            healthy_startup_vectors()
        ),
        expectations=tuple(
            healthy_startup_expectations()
        ),
    )

    test_case.validate()

    return test_case

def build_nominal_operation_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()

    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=0,
                ov=0,
                oc=0,
                ot=0,
            )
        )

        expectations.append(
            FPGAExpectation(
                timestamp=timestamp,
                state_code=2,
                fault_code=0,
                alarm=0,
                shutdown=0,
            )
        )

    test_case = EngineeringTestCase(
        test_id="TC-002",
        name="Nominal Operation",
        description=(
            "Verify the controller remains "
            "RUNNING with no active faults."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_brief_uv_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()

    vectors.extend([
        FPGATestVector(
            timestamp=3,
            reset=0,
            start=0,
            uv=1,
            ov=0,
            oc=0,
            ot=0,
        ),
        FPGATestVector(
            timestamp=4,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
        FPGATestVector(
            timestamp=5,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
    ])

    expectations.extend([
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
    ])

    test_case = EngineeringTestCase(
        test_id="TC-003",
        name="Brief Undervoltage Transient",
        description=(
            "Verify a one-cycle undervoltage "
            "does not cause FAULT or shutdown."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_sustained_uv_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()
        

    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=1,
                ov=0,
                oc=0,
                ot=0,
            )
        )

    expectations.extend([
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
            fault_code=1,
            alarm=1,
            shutdown=1,
        ),
    ])

    test_case = EngineeringTestCase(
        test_id="TC-004",
        name="Sustained Undervoltage",
        description=(
            "Verify sustained undervoltage "
            "passes persistence filtering and "
            "causes a latched FAULT."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_overcurrent_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()

    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=0,
                ov=0,
                oc=1,
                ot=0,
            )
        )

    expectations.extend([
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
    ])

    test_case = EngineeringTestCase(
        test_id="TC-005",
        name="Overcurrent Shutdown",
        description=(
            "Verify sustained overcurrent "
            "causes FAULT, stores OVERCURRENT, "
            "and asserts alarm and shutdown."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_overtemperature_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()


    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=0,
                ov=0,
                oc=0,
                ot=1,
            )
        )

    expectations.extend([
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
            fault_code=4,
            alarm=1,
            shutdown=1,
        ),
    ])

    test_case = EngineeringTestCase(
        test_id="TC-006",
        name="Overtemperature Shutdown",
        description=(
            "Verify sustained overtemperature "
            "causes FAULT and stores "
            "OVERTEMPERATURE."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_simultaneous_oc_ot_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()


    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=0,
                ov=0,
                oc=1,
                ot=1,
            )
        )

    expectations.extend([
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
    ])

    test_case = EngineeringTestCase(
        test_id="TC-007",
        name="Simultaneous OC and OT",
        description=(
            "Verify simultaneous overcurrent "
            "and overtemperature select "
            "OVERCURRENT according to the "
            "project fault-priority rule."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case

def build_reset_recovery_test() -> EngineeringTestCase:

    vectors = healthy_startup_vectors()

    expectations = healthy_startup_expectations()


    for timestamp in range(3, 7):

        vectors.append(
            FPGATestVector(
                timestamp=timestamp,
                reset=0,
                start=0,
                uv=0,
                ov=0,
                oc=1,
                ot=0,
            )
        )

    expectations.extend([
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
    ])

    vectors.append(
        FPGATestVector(
            timestamp=7,
            reset=1,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        )
    )

    expectations.append(
        FPGAExpectation(
            timestamp=7,
            state_code=4,
            fault_code=0,
            alarm=0,
            shutdown=0,
        )
    )

    test_case = EngineeringTestCase(
        test_id="TC-008",
        name="Fault Reset and Recovery",
        description=(
            "Verify reset from FAULT enters "
            "RECOVERY, clears the stored fault "
            "code, deasserts protection outputs, "
            "and returns to IDLE."
        ),
        vectors=tuple(vectors),
        expectations=tuple(expectations),
    )

    test_case.validate()

    return test_case


def build_engineering_test_cases() -> list[EngineeringTestCase]:

    test_cases = [
        build_normal_startup_test(),
        build_nominal_operation_test(),
        build_brief_uv_test(),
        build_sustained_uv_test(),
        build_overcurrent_test(),
        build_overtemperature_test(),
        build_simultaneous_oc_ot_test(),
        build_reset_recovery_test(),
    ]

    validate_test_catalog(
        test_cases
    )
    return test_cases

def validate_test_catalog(test_cases: list[EngineeringTestCase],) -> None:
    seen_ids = set()

    for test_case in test_cases:
        test_case.validate()

        if test_case.test_id in seen_ids:
            raise ValueError(
                "Duplicate test ID: "
            f"{test_case.test_id}"
        )

        seen_ids.add(
            test_case.test_id
        )

def print_test_catalog(test_cases: list[EngineeringTestCase],) -> None:

    print("========================================")
    print(" FPGA ENGINEERING TEST CATALOG")
    print("========================================")
    print("")

    DEFERRED_TESTS = {
        "TC-009": (
            "Failed Recovery — deferred until "
            "failed-recovery behaviour and its "
            "stimulus are formally defined."
        )
        }

    for test_case in test_cases:

        print(
            f"{test_case.test_id} | "
            f"{test_case.name}"
        )

        print(
            f"    {test_case.description}"
        )

        print(
            f"    Samples: "
            f"{len(test_case.vectors)}"
        )

        print("")


    for test_id, reason in DEFERRED_TESTS.items():

        print(
            f"{test_id} | DEFERRED"
        )

        print(
            f"    {reason}"
        )

if __name__ == "__main__":
        
    test_cases = (
        build_engineering_test_cases()
    )
        

    print_test_catalog(
        test_cases
    )