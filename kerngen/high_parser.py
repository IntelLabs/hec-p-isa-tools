# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from enum import Enum
from typing import NamedTuple


class Scheme(Enum):
    """Enum class representing valid FHE Schemes"""

    BGV = "BGV"
    CKKS = "CKKS"


def parse_inputs(lines: list[str]) -> list:
    """parse the inputs given in return list of data and operations"""

    # Check first command parsed is CONTEXT
    if lines[0].split(" ", 1)[0].lower() != "context":
        raise RuntimeError(f"First command must be `CONTEXT`, given `{lines[0]}`")

    def delegate(command_str):
        command, rest = command_str.split(" ", 1)
        match command.lower():
            case "context":
                return Context.from_string(rest)
            case "data":
                return Data.from_string(rest)
            case _:
                return Command.from_string(command_str)

    return list(map(delegate, lines))


class Context(NamedTuple):
    """Class representing a given context of the scheme"""

    scheme: Scheme
    poly_order: int  # the N
    max_rns: int

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        inputs = line.split()
        return cls(
            scheme=Scheme(inputs[0]), poly_order=int(inputs[1]), max_rns=int(inputs[2])
        )


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
