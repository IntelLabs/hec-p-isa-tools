# Copyright (C) 2024 Intel Corporation

"""Test the expected behaviour of the kerngen script"""

from enum import Enum
from pathlib import Path
from subprocess import run
import pytest


class Op(Enum):
    """Enum class of valid high opnames and corresponding low ops"""

    ADD = "add"
    MUL = "mul"


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


@pytest.mark.parametrize("gen_op_data", ["ADD", "MUL"], indirect=True)
def test_op(kerngen_path, gen_op_data):
    """Test kerngen outputs correct data based on input for various operations"""
    input_string, expected_out = gen_op_data
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    assert expected_out in result.stdout
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
    assert "RuntimeError: No `CONTEXT` provided before `ADD a b c`" in result.stderr
    assert result.returncode != 0


def test_multiple_contexts(kerngen_path):
    """Test kerngen raises an exception when more than one context is given"""
    input_string = "CONTEXT BGV 8192 4\nData a 2\nCONTEXT BGV 8192 4\n"
    result = execute_process(
        [kerngen_path],
        data_in=input_string,
    )
    assert not result.stdout
    assert "RuntimeError: Second context given" in result.stderr
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
    assert "GeneratorError: Scheme `SCHEME` not found in manifest file" in result.stderr
    assert result.returncode != 0


@pytest.fixture(name="gen_op_data")
def fixture_gen_op_data(request):
    """Given an op name, return both the input and expected output strings"""
    in_lines = (
        "CONTEXT BGV 8192 4",
        "Data a 2",
        "Data b 2",
        "Data c 2",
        f"{request.param} a b c",
    )
    # TODO: Build this string properly
    out = f"0, {Op[request.param].value}, a_0_0_0, b_0_0_0, c_0_0_0, 0"
    return "\n".join(in_lines), out


@pytest.fixture(name="kerngen_path")
def fixture_kerngen_path() -> Path:
    """Returns the absolute path to the `kerngen.py` script"""
    return Path(__file__).resolve().parent.parent / "kerngen.py"
