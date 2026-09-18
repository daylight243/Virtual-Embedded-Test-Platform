import pytest
from pathlib import Path
from fpga_results import (
    FPGA_result,
    validate_input_output_alignment,
    read_FPGA_results
)
def test_matching_timestamps_are_accepted():
    results = [
        FPGA_result(
            timestamp=0,
            state_code=0,
            fault_code=0,
            alarm=0,
            shutdown=0,
        ),
        FPGA_result(
            timestamp=1,
            state_code=1,
            fault_code=0,
            alarm=0,
            shutdown=0,
        )
    ]

    validate_input_output_alignment(
        input_timestamps=[0, 1],
        results=results,
    )
def test_missing_output_timestamp_is_rejected():
    results = [
        FPGA_result(
            timestamp=0,
            state_code=0,
            fault_code=0,
            alarm=0,
            shutdown=0,
        )
    ]
    with pytest.raises(ValueError):
        validate_input_output_alignment(
            input_timestamps=[0, 1],
            results=results,
        )

def test_result_parser_reads_known_row(
    tmp_path: Path,
):
    output_file = tmp_path / "outputs.csv"
    output_file.write_text(
        "timestamp,state_code,fault_code,"
        "alarm,shutdown\n"
        "6,3,3,1,1\n",
        encoding="utf-8",
    )
    results = read_FPGA_results(
        output_file
    )
    assert len(results) == 1
    assert results[0].timestamp == 6
    assert results[0].state_code == 3
    assert results[0].fault_code == 3
    assert results[0].alarm == 1
    assert results[0].shutdown == 1  

def test_result_parser_rejects_bad_integer(
    tmp_path: Path,
):
    output_file = tmp_path / "outputs.csv"
    output_file.write_text(
        "timestamp,state_code,fault_code,"
        "alarm,shutdown\n"
        "6,3,FAULT,1,1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        read_FPGA_results(
            output_file
        )

def test_missing_result_file_is_not_silent(
    tmp_path,
):
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        read_FPGA_results(missing)