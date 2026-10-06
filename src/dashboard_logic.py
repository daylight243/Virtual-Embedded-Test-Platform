STATE_NAMES = {
    0: "IDLE",
    1: "STARTUP",
    2: "RUNNING",
    3: "FAULT",
    4: "RECOVERY",
}


FAULT_NAMES = {
    0: "NONE",
    1: "UV",
    2: "OV",
    3: "OC",
    4: "OT",
}


def state_name(
    state_code: int,
) -> str:
    return STATE_NAMES.get(
        state_code,
        f"UNKNOWN ({state_code})",
    )


def fault_name(
    fault_code: int,
) -> str:
    return FAULT_NAMES.get(
        fault_code,
        f"UNKNOWN ({fault_code})",
    )


def verification_name(
    passed: bool,
) -> str:
    return (
        "PASS"
        if passed
        else "FAIL"
    )


def find_state_transitions(
    outputs,
):
    transitions = []

    previous_state = None

    for output in outputs:
        current_state = (
            output["state_code"]
        )

        if current_state != previous_state:
            transitions.append(
                {
                    "Timestamp":
                        output["timestamp"],

                    "State":
                        state_name(
                            current_state
                        ),

                    "State Code":
                        current_state,
                }
            )

            previous_state = (
                current_state
            )

    return transitions


def find_fault_transitions(
    outputs,
):
    transitions = []

    previous_fault = None

    for output in outputs:
        current_fault = (
            output["fault_code"]
        )

        if current_fault != previous_fault:
            transitions.append(
                {
                    "Timestamp":
                        output["timestamp"],

                    "Fault":
                        fault_name(
                            current_fault
                        ),

                    "Fault Code":
                        current_fault,
                }
            )

            previous_fault = (
                current_fault
            )

    return transitions