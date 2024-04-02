# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

import math
from pathlib import Path
from typing import NamedTuple, Iterator

from generators import Generators
from highop import HighOp
from polys import Polys


MANIFEST_FILE = Path(__file__).parent / "pisa_generators/manifest.json"

Symbol = str


class Comment(NamedTuple):
    """Holder of a comment line"""

    comment: str


class EmptyLine(NamedTuple):
    """Holder of an empty line"""


class Context(NamedTuple):
    """Class representing a given context of the scheme"""

    scheme: str
    poly_order: int  # the N
    max_rns: int

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        scheme, poly_order, max_rns = line.split()
        int_poly_order = int(poly_order)
        int_max_rns = int(max_rns)
        return cls(
            scheme=scheme.upper(),
            poly_order=int_poly_order,
            max_rns=int_max_rns,
        )

    @property
    def ntt_stages(self):
        """Returns NTT stages (== log2(N))"""
        return int(math.log2(self.poly_order))

    @property
    def units(self):
        """units based on 8192 ~ 8K sized polynomials"""
        return max(1, self.poly_order // 8192)


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str
    parts: int

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, parts = line.split()
        return cls(name=name, parts=int(parts))


class Immediate(NamedTuple):
    """Class representing a Immediate type with related attributes"""

    name: str

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, *rest = line.split()
        if len(rest) > 0:
            raise ValueError("Immediate only has a name; no other arguments")
        return cls(name=name)


ParserType = Context | Data | EmptyLine | Comment | HighOp


class ParseResults:
    """Queryable class about parse results"""

    def __init__(self, iterable, symbols_map):
        self._commands = list(iterable)
        self._symbols_map = symbols_map

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
    def symbols_map(self):
        """Return the polys map built from data definitions"""
        return self._symbols_map

    def get_pisa_ops(self) -> Iterator[list[HighOp]]:
        """generator returns lists of p-isa instructions"""
        commands = self._commands
        return (
            command.to_pisa() if isinstance(command, HighOp) else None
            for command in commands
        )


# pylint: disable=too-few-public-methods
class Parser:
    """Parser for input high operations to p-isa operations"""

    def __init__(self) -> None:
        """holds kernel generators and is able to parser high operations script"""
        self.generators: Generators | None = None

    def set_generator(self, scheme: str) -> None:
        """Set generator once context is known"""
        self.generators = Generators.from_manifest(MANIFEST_FILE, scheme)

    def _delegate(self, command_str: str, context_seen: list[Context], symbols_map):
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
                context_seen.append(context)
                self.set_generator(context.scheme)
                return context
            case "#":
                return Comment(comment=command_str)
            case "imm":
                immediate = Immediate.from_string(rest)
                symbols_map[immediate.name] = immediate
                return immediate
            case "data":
                # Poly starts with max rns
                context = context_seen[0]  # assume 1 element
                # Populate the polys map
                data = Data.from_string(rest)
                symbols_map[data.name] = Polys(
                    name=data.name, parts=data.parts, rns=context.max_rns
                )
                return data
            case _:
                # If context has not been given yet - FAIL
                if len(context_seen) == 0:
                    raise RuntimeError(
                        f"No `CONTEXT` provided before `{command_str.rstrip()}`"
                    )

                # Look up commands defined in manifest
                if self.generators is None:
                    raise ValueError("Generator not set")

                cls = self.generators.get_pisa_op(command)
                return cls.from_string(context_seen[0], symbols_map, rest)

    def parse_inputs(self, lines: list[str]) -> ParseResults:
        """parse the inputs given in return list of data and operations"""

        symbols_map: dict[Symbol, Polys | Immediate] = {}
        context_seen: list[Context] = []
        commands = (self._delegate(line, context_seen, symbols_map) for line in lines)
        return ParseResults(commands, symbols_map)
