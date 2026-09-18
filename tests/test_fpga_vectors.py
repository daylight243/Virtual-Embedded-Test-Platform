from pathlib import Path
from fpga_vectors import FPGATestVector, write_vectors
def test_vector_writer_preserves_field_order(tmp_path: Path):
    output_file = tmp_path / "inputs.csv"
    vectors = [
        FPGATestVector(
            timestamp=3,
            reset=0,
            start=0,
            uv=1,
            ov=0,
            oc=0,
            ot=0,
        )
    ]
    write_vectors(
        vectors,
        output_file,
    )
    lines = output_file.read_text(
        encoding="utf-8"
    ).splitlines()
    assert lines[0] == (
        "timestamp,reset,start,uv,ov,oc,ot"
    )
    assert lines[1] == (
        "3,0,0,1,0,0,0"
    )