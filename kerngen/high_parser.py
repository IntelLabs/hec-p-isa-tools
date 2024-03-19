# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from enum import Enum
from typing import NamedTuple

from generators import Generators


class Scheme(Enum):
    """Enum class representing valid FHE Schemes"""

    BGV = "BGV"
    CKKS = "CKKS"


def parse_inputs(
    lines: list[str], manifest_path="./pisa_generators/manifest.json"
) -> list:
    """parse the inputs given in return list of data and operations"""

    generators = Generators.from_manifest(manifest_path)

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
                # Look up commands defined in manifest
                cls = generators.get_pisa_op(command)
                return cls.from_string(rest)

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
            scheme=Scheme(scheme.upper()),
            poly_order=int(poly_order),
            max_rns=int(max_rns),
        )


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str
    parts: int

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, parts = line.split()
        return cls(name=name, parts=int(parts))
