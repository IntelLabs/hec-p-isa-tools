# Copyright (C) 2024 Intel Corporation

"""Test the expected behaviour of the kerngen script"""

from pathlib import Path
from subprocess import run
import pytest


def execute_process(cmd: list[str], data_in=None):
    """Helper function for executing processes. stdout and stderr are always
    captured. NOTE: subprocess.run will fail silently with a non-zero exit code
    so always check the returncode"""
    return run(
        list(map(str, cmd)),
        input=data_in,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


def test_add(kerngen_path):
    """Test kerngen outputs correct data based on input"""
    input_string = "CONTEXT BGV 8192 4\nData a 2\nData b 2\nData c 2\nADD a b c\n"
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    # TODO: Check the expected string
    assert result.stdout
    assert not result.stderr
    assert result.returncode == 0


def test_missing_context(kerngen_path):
    """Test kerngen raises an exception when context is not the first line of
    input"""
    input_string = "ADD a b c\nCONTEXT BGV 8192 4\n"
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    assert not result.stdout
    assert "First command must be `CONTEXT`" in result.stderr
    assert result.returncode != 0


def test_unrecognised_opname(kerngen_path):
    """Test kerngen raises an exception when receiving an unrecognised
    opname"""
    input_string = "CONTEXT BGV 8192 4\nOPERATION a b c\n"
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    assert not result.stdout
    assert (
        "GeneratorError: Op not found in available pisa ops: OPERATION" in result.stderr
    )
    assert result.returncode != 0


def test_invalid_scheme(kerngen_path):
    """Test kerngen raises an exception when receiving an invalid scheme"""
    input_string = "CONTEXT SCHEME 8192 4\nADD a b c\n"
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    assert not result.stdout
    assert "ValueError: 'SCHEME' is not a valid Scheme" in result.stderr
    assert result.returncode != 0


@pytest.fixture(name="kerngen_path")
def fixture_kerngen_path() -> Path:
    """Returns the absolute path to the `kerngen.py` script"""
    return Path(__file__).resolve().parent.parent / "kerngen.py"
