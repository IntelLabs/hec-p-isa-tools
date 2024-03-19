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
    if not lines[0].lower().startswith("context"):
        raise RuntimeError(f"First command must be `CONTEXT`, given `{lines[0]}`")

    def delegate(command_str):
        try:
            # the split removes leading whitespace
            command, rest = command_str.split(maxsplit=1)
        except ValueError:
            return EmptyLine()

        match command.lower():
            case "context":
                return Context.from_string(rest)
            case "data":
                return Data.from_string(rest)
            case "#":
                return Comment(comment=command_str)
            case _:
                return Command.from_string(command_str)

    return list(map(delegate, lines))


class Comment(NamedTuple):
    """Holder of a comment line"""

    comment: str


class EmptyLine(NamedTuple):
    """Holder of an empty line"""


class Context(NamedTuple):
    """Class representing a given context of the scheme"""

    scheme: Scheme
    poly_order: int  # the N
    max_rns: int

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        scheme, poly_order, max_rns = line.split()
        return cls(
            scheme=Scheme(scheme), poly_order=int(poly_order), max_rns=int(max_rns)
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
            return cls(op=op, output=output, inputs=inputs)
        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{line}`") from e


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        return cls(name=line)
