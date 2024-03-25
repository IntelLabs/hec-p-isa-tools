# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from enum import Enum
from pathlib import Path
from typing import NamedTuple, Iterator

from generators import Generators
from highop import HighOp
from polys import Polys


MANIFEST_FILE = Path(__file__).parent / "pisa_generators/manifest.json"

Symbol = str


class Scheme(Enum):
    """Enum class representing valid FHE Schemes"""

    BGV = "BGV"
    CKKS = "CKKS"


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

    @property
    def units(self):
        """units based on 8192 ~ 8K sized polynomials"""
        # TODO remove hardcoding
        # UNIT_SIZE = 13
        # NUNITS = 8
        # N = 8192
        # batch_size = 8 if N <= (UNIT_SIZE << 1) else max(1, 8 // NUNITS)
        return 1


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str
    parts: int

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, parts = line.split()
        return cls(name=name, parts=int(parts))


ParserType = Context | Data | EmptyLine | Comment | HighOp


class ParseResults:
    """Queryable class about parse results"""

    def __init__(self, iterable, polys_map):
        self._commands = list(iterable)
        self._polys_map = polys_map

    @property
    def context(self):
        """Return found context"""
        return next(
            context for context in self._commands if isinstance(context, Context)
        )

    @property
    def commands(self):
        """Return all parsed lines"""
        return self._commands

    @property
    def polys_map(self):
        """Return the polys map built from data definitions"""
        return self._polys_map

    def get_pisa_ops(self) -> Iterator[list[HighOp]]:
        """generator returns lists of p-isa instructions"""
        commands = self._commands
        return (
            command.to_pisa() if isinstance(command, HighOp) else None
            for command in commands
        )


class Parser:
    """Parser for input high operations to p-isa operations"""

    def __init__(self, generators: Generators = None) -> None:
        """holds kernel generators and is able to parser high operations script"""
        self.generators = (
            generators
            if generators is not None
            else Generators.from_manifest(MANIFEST_FILE)
        )

    def _delegate(self, command_str: str, context_seen: set[Context], polys_map):
        """This helper is delegated the task of which subparser objects to create.
        It is also responsible for setting context."""
        try:
            # the split removes leading whitespace
            command, rest = command_str.split(maxsplit=1)
        except ValueError:
            return EmptyLine()

        match command.lower():
            case "context":
                if len(context_seen) != 0:
                    raise RuntimeError("Second context given")
                context = Context.from_string(rest)
                context_seen.add(context)
                return context
            case "#":
                return Comment(comment=command_str)
            case "data":
                # Populate the polys map
                data = Data.from_string(rest)
                polys_map[data.name] = Polys(*data)
                return data
            case _:
                # If context has not been given yet - FAIL
                if len(context_seen) == 0:
                    raise RuntimeError(
                        f"No `CONTEXT` provided before `{command_str.rstrip()}`"
                    )

                # Look up commands defined in manifest
                cls = self.generators.get_pisa_op(command)
                return cls.from_string(next(iter(context_seen)), polys_map, rest)

    def parse_inputs(self, lines: list[str]) -> ParseResults:
        """parse the inputs given in return list of data and operations"""

        polys_map: dict[Symbol, Data] = {}
        context_seen: set[Context] = set()
        commands = (self._delegate(line, context_seen, polys_map) for line in lines)
        return ParseResults(commands, polys_map)
