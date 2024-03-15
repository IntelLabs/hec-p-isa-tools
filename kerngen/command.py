# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from typing import NamedTuple


class Command(NamedTuple):
    """Class representing a command consisting of an operation with input(s) and
    output"""

    op: str
    inputs: list[str]
    output: str

    @classmethod
    def from_string(cls, op: str, inputs: list[str], output: str):
        """Construct the command from a string of the form `opname output
        inputs`"""
        return cls(op=op, inputs=inputs, output=output)
