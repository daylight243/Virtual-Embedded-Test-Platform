import pytest
from fpga_fault_injection import FaultInjection, apply_fault_injections
from fpga_vectors import FPGATestVector
def test_fault_injection_end_timestamp():
    injection = FaultInjection(
        fault="overcurrent",
        start_timestamp=3,
        duration=4,
    )
    assert injection.fault == "overcurrent"
    assert injection.end_timestamp_exclusive == 7

def test_duration_one_is_active_once():
    injection = FaultInjection(
        fault="undervoltage",
        start_timestamp=3,
        duration=1,
    )
    assert injection.active_at(2) is False
    assert injection.active_at(3) is True
    assert injection.active_at(4) is False

def test_duration_four_is_active_at_t3_through_t6():
    injection = FaultInjection(
        fault="overcurrent",
        start_timestamp=3,
        duration=4,
    )
    assert injection.active_at(2) is False
    assert injection.active_at(3) is True
    assert injection.active_at(4) is True
    assert injection.active_at(5) is True
    assert injection.active_at(6) is True
    assert injection.active_at(7) is False

def test_overlapping_faults_preserve_both_bits():
    vectors = [
        FPGATestVector(
            timestamp=3,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        )
    ]
    injections = [
        FaultInjection(
            fault="overcurrent",
            start_timestamp=3,
            duration=1,
        ),
        FaultInjection(
            fault="overtemperature",
            start_timestamp=3,
            duration=1,
        ),
    ]
    result = apply_fault_injections(
        vectors=vectors,
        injections=injections,
    )
    assert result[0].oc == 1
    assert result[0].ot == 1

def test_zero_duration_is_rejected():
    injection = FaultInjection(
        fault="overcurrent",
        start_timestamp=3,
        duration=0,
    )
    with pytest.raises(ValueError):
        injection.validate()

def test_negative_start_is_rejected():
    injection = FaultInjection(
        fault="overcurrent",
        start_timestamp=-1,
        duration=1,
    )
    with pytest.raises(ValueError):
        injection.validate()

def test_unknown_fault_is_rejected():
    injection = FaultInjection(
        fault="fire",
        start_timestamp=3,
        duration=1,
    )
    with pytest.raises(ValueError):
        injection.validate()

