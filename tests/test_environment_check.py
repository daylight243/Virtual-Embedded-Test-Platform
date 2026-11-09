from unittest.mock import patch

import environment_check


def test_python_version_supported():
    assert environment_check.check_python_version()


def test_required_directories_exist():
    assert environment_check.check_directories()


def test_required_files_exist():
    assert environment_check.check_files()


def test_missing_simulator_is_reported():
    with patch(
        "environment_check.shutil.which",
        return_value=None,
    ):
        result = (
            environment_check.check_executables()
        )

    assert result is False


def test_available_simulator_is_reported():
    with patch(
        "environment_check.shutil.which",
        return_value="C:/Tools/simulator.exe",
    ):
        result = (
            environment_check.check_executables()
        )

    assert result is True