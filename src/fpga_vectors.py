from dataclasses import dataclass
from pathlib import Path

@dataclass 
class FPGATestVector:
    timestamp: int
    reset: int
    start: int
    uv: int
    ov: int
    oc: int
    ot: int
    def to_csv_row(self) -> str:
        return(

               f"{self.timestamp},"
               f"{self.reset},"
               f"{self.start},"
               f"{self.uv},"
               f"{self.ov},"
               f"{self.oc},"
               f"{self.ot}"
        )
    def validate_bit(self, name: str, value: int) -> None:
        if value not in (0, 1):
            raise ValueError (
              f"{name} must be 0 or 1 got value {value}"  
            )
    def validate(self) -> None:
        if self.timestamp < 0:
            raise ValueError(
                f"timestamp must be non-negative, got {self.timestamp}"
            )

        self.validate_bit("reset", self.reset)
        self.validate_bit("start", self.start)
        self.validate_bit("uv", self.uv)
        self.validate_bit("ov", self.ov)
        self.validate_bit("oc", self.oc)
        self.validate_bit("ot", self.ot)

vector = FPGATestVector(
       timestamp=3,
    reset=0,
    start=0,
    uv=0,
    ov=0,
    oc=1,
    ot=0,
)

vector.validate()

print(vector.to_csv_row())

def build_demo_vectors() -> list[FPGATestVector]:
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
        FPGATestVector(
            timestamp=3,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=1,
            ot=0,
        ),
        FPGATestVector(
            timestamp=4,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=1,
            ot=0,
        ),
        FPGATestVector(
            timestamp=5,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=1,
            ot=0,
        ),
        FPGATestVector(
            timestamp=6,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=1,
            ot=0,
        ),
        FPGATestVector(
            timestamp=7,
            reset=0,
            start=0,
            uv=0,
            ov=0,
            oc=0,
            ot=0,
        ),
    ]
CSV_HEADER = "timestamp,reset,start,uv,ov,oc,ot"
def write_vectors(
    vectors: list[FPGATestVector],
    output_path: Path,
) -> None:
    lines = [CSV_HEADER]

    for vector in vectors:
        vector.validate()
        lines.append(vector.to_csv_row())

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

def vector_from_csv_row(row: str) -> FPGATestVector:
    parts = row.strip().split(",")

    if len(parts) != 7:
        raise ValueError ( 
        f"Expected 7 fields, got {len(parts)}: {row}"
        )
    vector = FPGATestVector(
        timestamp=int(parts[0]),
        reset=int(parts[1]),
        start=int(parts[2]),
        uv=int(parts[3]),
        ov=int(parts[4]),
        oc=int(parts[5]),
        ot=int(parts[6]),
    )

    vector.validate()

    return vector

def read_vectors (input_path: Path) -> list[FPGATestVector]:
    lines = input_path.read_text (encoding = "utf-8").splitlines()

    if not lines: 
        raise ValueError(
            "Unexpected FPGA input header"
        )
    vectors = []

    for line in lines[1:]:
        if not line.strip:
            continue

        vectors.append (vector_from_csv_row(line))

    return vectors
            


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    output_path = project_root / "build" / "fpga_inputs.csv"

    original_vectors = build_demo_vectors()

    write_vectors(
        vectors=original_vectors,
        output_path=output_path,
    )

    loaded_vectors = read_vectors(output_path)

    
    print("FPGA input vectors created:")
    print(output_path)

    print("")
    print("Generated vectors:")

    for vector in original_vectors:
        print(vector.to_csv_row())

    if original_vectors == loaded_vectors:
        print("VECTOR ROUND-TRIP RESULT: PASS")
    else:
        print("VECTOR ROUND-TRIP RESULT: FAIL")


if __name__ == "__main__":
        main()