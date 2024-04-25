# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

from pathlib import Path
from typing import Iterator

from .generators import Generators
from .pisa_operations import PIsaOp
from .types import Context, Comment, EmptyLine, Data, Immediate, Polys, HighOp

MANIFEST_FILE = str(
    Path(__file__).parent.parent.absolute() / "pisa_generators/manifest.json"
)

Symbol = str


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

    def get_pisa_ops(self) -> Iterator[list[PIsaOp] | None]:
        """generator returns lists of p-isa instructions"""
        commands = self._commands
        return (
            command.to_pisa() if isinstance(command, HighOp) else None
            for command in commands
        )


class Parser:
    """Parser for input high operations to p-isa operations"""

    def __init__(self) -> None:
        """holds kernel generators and is able to parser high operations script"""
        self.generators: Generators | None = None

    def set_generator(self, scheme: str) -> None:
        """Set generator once context is known"""
        self.generators = Generators.from_manifest(MANIFEST_FILE, scheme)

    def _get_label(self, command_str: str):
        """Helper function for grabbing the label if one exists else return a default value."""
        label = "0"
        if ":" in command_str:
            label, command_str = command_str.split(":")
        return label, command_str

    def _delegate(self, command_str: str, context_seen: list[Context], symbols_map):
        """This helper is delegated the task of which subparser objects to create.
        It is also responsible for setting context."""
        label, command_str = self._get_label(command_str)
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
                return cls.from_string(context_seen[0], symbols_map, rest, label=label)

    def parse_inputs(self, lines: list[str]) -> ParseResults:
        """parse the inputs given in return list of data and operations"""

        symbols_map: dict[Symbol, Polys | Immediate] = {}
        context_seen: list[Context] = []
        commands = (self._delegate(line, context_seen, symbols_map) for line in lines)
        return ParseResults(commands, symbols_map)
