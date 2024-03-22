# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
import itertools as it

from pisa_operations import Add as PisaAdd, PIsaOp
from polys import Polys
from .highop import HighOp


@dataclass
class Add(HighOp):
    """Class representing the high-level addition operation"""

    output: str
    inputs: list[str]

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa  equivalent of an Add"""

        # TODO These need to be given by Context
        units = 1
        parts = 2
        rns = 4

        rout = Polys(self.output, parts, units)
        rin0 = Polys(self.inputs[0], parts, units)
        rin1 = Polys(self.inputs[1], parts, units)

        return [
            PisaAdd(
                rout.expand(part, q, unit),
                rin0.expand(part, q, unit),
                rin1.expand(part, q, unit),
                q,
            )
            for q, part, unit in it.product(range(rns), range(parts), range(units))
        ]

    @classmethod
    def from_string(cls, args_line: str):
        """Construct context from args string"""
        try:
            output, *inputs = args_line.split()
            return cls(output=output, inputs=inputs)
        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e
