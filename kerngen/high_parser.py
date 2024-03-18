# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from typing import NamedTuple


def parse_inputs(lines: list[str]) -> list:
    """parse the inputs given in return list of data and operations"""
    return list(map(Command.from_string, lines))


class Context(NamedTuple):
    """Class representing a given context of the scheme"""

    scheme: str
    poly_order: int  # the N
    max_rns: int

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        inputs = line.split()
        return cls(scheme=inputs[0], poly_order=int(inputs[1]), max_rns=int(inputs[2]))


class Command(NamedTuple):
    """Class representing a command consisting of an operation with input(s) and
    output"""

    op: str
    output: str
    inputs: list[str]

    @classmethod
    def from_string(cls, line: str):
        """Construct the command from a string of the form `opname output
        inputs`"""
        try:
            op, output, *inputs = line.split()
        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{line}`") from e
        return cls(op=op, output=output, inputs=inputs)


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        return cls(name=line)
