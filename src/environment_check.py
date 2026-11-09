from pathlib import Path
import importlib.util
import shutil
import sqlite3
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = (
    "src",
    "hdl",
    "sql",
    "tests",
    "dashboard",
)

REQUIRED_FILES = (
    "requirements.txt",
    "pytest.ini",
    "sql/schema.sql",
    "src/persistent_campaign.py",
    "src/fpga_runner.py",
)

PYTHON_MODULES = (
    "pytest",
    "streamlit",
    "boto3",
)

SIMULATOR_TOOLS = (
    "iverilog",
    "vvp",
)

OPTIONAL_TOOLS = (
    "gtkwave",
)


def check_python_version() -> bool:
    version = sys.version_info

    supported = version >= (3, 10)

    print(
        f"Python: {sys.version.split()[0]}"
    )

    if supported:
        print("  Status: OK")
    else:
        print("  Status: Python 3.10+ required")

    return supported


def check_directories() -> bool:
    print("\nProject directories:")

    all_found = True

    for name in REQUIRED_DIRECTORIES:
        path = PROJECT_ROOT / name

        exists = path.is_dir()

        print(
            f"  {'OK' if exists else 'MISSING'}: {name}"
        )

        if not exists:
            all_found = False

    return all_found


def check_files() -> bool:
    print("\nRequired project files:")

    all_found = True

    for name in REQUIRED_FILES:
        path = PROJECT_ROOT / name

        exists = path.is_file()

        print(
            f"  {'OK' if exists else 'MISSING'}: {name}"
        )

        if not exists:
            all_found = False

    return all_found


def check_python_modules() -> bool:
    print("\nPython packages:")

    all_found = True

    for module_name in PYTHON_MODULES:
        found = (
            importlib.util.find_spec(module_name)
            is not None
        )

        print(
            f"  {'OK' if found else 'MISSING'}: "
            f"{module_name}"
        )

        if not found:
            all_found = False

    return all_found


def check_sqlite() -> bool:
    print("\nSQLite:")

    try:
        connection = sqlite3.connect(":memory:")

        version = connection.execute(
            "SELECT sqlite_version()"
        ).fetchone()[0]

        connection.close()

        print(f"  OK: SQLite {version}")

        return True

    except sqlite3.Error as error:
        print(
            f"  FAILED: {error}"
        )

        return False


def check_executables() -> bool:
    print("\nSimulator tools:")

    all_found = True

    for name in SIMULATOR_TOOLS:
        executable = shutil.which(name)

        if executable:
            print(f"  OK: {name} -> {executable}")
        else:
            print(f"  MISSING: {name}")
            all_found = False

    print("\nOptional tools:")

    for name in OPTIONAL_TOOLS:
        executable = shutil.which(name)

        if executable:
            print(f"  OK: {name} -> {executable}")
        else:
            print(f"  NOT FOUND: {name}")

    return all_found


def main() -> int:
    print("=" * 50)
    print("VETP Version 1 — Environment Preflight")
    print("=" * 50)

    results = {
        "Python version": check_python_version(),
        "Directories": check_directories(),
        "Files": check_files(),
        "Python packages": check_python_modules(),
        "SQLite": check_sqlite(),
        "Simulator tools": check_executables(),
    }

    print("\n" + "=" * 50)
    print("Preflight summary")
    print("=" * 50)

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")

    if all(results.values()):
        print("\nEnvironment preflight passed.")
        return 0

    print("\nEnvironment requires attention.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())